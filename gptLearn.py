import os
import sys
import argparse
from llama_index import GPTVectorStoreIndex, Document, SimpleDirectoryReader, StorageContext, load_index_from_storage
import requests
from bs4 import BeautifulSoup
import re
import shutil
from datetime import datetime
import pandas as pd
import fnmatch
import PyPDF2

#this program can process pdf,excel,word,txt,html,csv, url, 

data_dir = "./data"
not_learn=os.path.join(data_dir, 'not_learning')

def extract_text_from_pdf(file):
    # Check if the file is located in the data directory
    if os.path.isfile(os.path.join(data_dir, file)) and file.endswith(".pdf"):
        # Open the PDF file in read-binary mode
        with open(os.path.join(data_dir, file), "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            
            # Extract text from each page of the PDF
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            
            # Save the extracted text into a text file
            txt_file = file.replace(".pdf", ".txt")
            with open(os.path.join(data_dir, txt_file), "w") as txt_file:
                txt_file.write(text)
        
        # Move the PDF file to the "not_learn" folder
        os.rename(os.path.join(data_dir, file), os.path.join(not_learn, file))
        

def extract_text_from_excel(file):
    # Convert Excel file to CSV
    df = pd.read_excel(os.path.join(data_dir, file), engine='openpyxl')
    csv_file = file.replace(".xlsx", ".csv")
    df.to_csv(os.path.join(data_dir, csv_file), index=False)

   # Move the Excel file to the "not learned" folder
    os.rename(os.path.join(data_dir, file), os.path.join(not_learn, file))

 
def extract_text_from_url(url, output_dir="./data"):
    response = requests.get(url)

    # Raise exception if the request was unsuccessful
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get the text
    text = soup.get_text()

    # Break into lines and remove leading and trailing whitespaces
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    # Get page title and make it a safe string for a filename
    title = soup.title.string
    title = re.sub('[\W_]+', '_', title)

    # Append timestamp for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{title}_{timestamp}.txt"

    # Save the text into a file
    with open(os.path.join(output_dir, filename), 'w') as f:
        f.write(text)


class AddingDataToGPT:
    def __init__(self, retrain=False):
        self.index = None
        self.persist_dir = "./storage"
        self.data_dir = data_dir
        if not any(fname for fname in os.listdir(data_dir) if fname != '.gitignore' and not os.path.isdir(
                os.path.join(data_dir, fname))):
            print("No files to learn from in the 'data' directory. Exiting the program.")
            sys.exit()
        if os.path.exists(self.persist_dir) and not retrain:
            self.read_from_storage()
        else:
            self.build_storage()
        self.query_engine = self.index.as_query_engine()

    def add_conversation_to_storage(self, question, response):
        # Create a new document with the provided question and response
        document = [{"question": question, "response": response}]
        self.index = GPTVectorStoreIndex.from_documents(documents)
        self.index.storage_context.persist()

    def build_storage(self):
        print("please wait...")
        documents = []
        if not os.path.exists(os.path.join(data_dir, 'not_learning')):
            os.makedirs(os.path.join(data_dir, 'not_learning'))

        for filename in os.listdir(data_dir):
            if os.path.isfile(os.path.join(data_dir, filename)):
                if filename == ".gitignore" or filename.startswith(".~lock"):
                    continue
                elif filename.endswith((".xls", ".xlsx")):
                    extract_text_from_excel(filename)
                    print("Learned:", filename)
                elif filename.endswith(".pdf"):
                    extract_text_from_pdf(filename)
                    print("Learned:", filename)
                elif filename.endswith((".txt", ".html")):
                    print("Learned:", filename)
                else:
                    shutil.move(os.path.join(data_dir, filename), os.path.join(data_dir, "not_learn"))
                    print(f"Warning: Ignoring file \033[91m{filename}\033[0m because it does not have a supported file extension.")

        document = SimpleDirectoryReader(os.path.join(self.data_dir)).load_data()
        documents.extend(document)
        self.index = GPTVectorStoreIndex.from_documents(documents)
        self.index.storage_context.persist()

    def read_from_storage(self):
        storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
        self.index = load_index_from_storage(storage_context)

    def run_conversation(self):
        while True:
            question = input("Enter your question (or 'exit' to quit): ")
            if question.lower() == "exit":
                break

            if question.lower() == "learn!":
                self.build_storage()
                self.read_from_storage()
                print("learning done")
            else:
                self.query_engine = self.index.as_query_engine()
                response = self.query_engine.query(question)
                print(f"\033[1;32m{response}\033[0m")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--train", action="store_true", help="Retrain the model")
    parser.add_argument("-u", "--url", type=str, help="URL to extract text from")
    return parser.parse_args()


def main():
    # print(data_dir)
    args = parse_arguments()

    if args.url:
        extract_text_from_url(args.url)
        args.train = True

    if args.train:
        adding_data = AddingDataToGPT(retrain=True)
    else:
        adding_data = AddingDataToGPT()
    adding_data.run_conversation()


if __name__ == "__main__":
    main()
