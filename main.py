#!/usr/bin/python3
import os
import openai
import sys
import argparse
from llama_index import GPTVectorStoreIndex, Document, SimpleDirectoryReader,StorageContext,load_index_from_storage
import requests
from bs4 import BeautifulSoup
import re
import shutil

openai.api_key=os.environ['OPENAI_API_KEY']

def extract_text_from_url(url, output_file="output1.txt"):
    print(url)
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

    # Save the text into a file
    with open(output_file, 'w') as f:
        f.write(text)


class AddingDataToGPT:
    def __init__(self, retrain=False):
        self.index = None
        self.persist_dir = "./storage"
        self.data_dir = "./data"
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
        if not os.path.exists(os.path.join(self.data_dir, 'not_learning')):
            os.makedirs(os.path.join(self.data_dir, 'not_learning'))
        
        for filename in os.listdir(self.data_dir):
            if os.path.isfile(os.path.join(self.data_dir, filename)):
                if filename == ".gitignore" or filename.startswith(".~lock"):
                    continue
                if not filename.endswith((".doc", ".docx", ".txt", ".html")):
                    shutil.move(os.path.join(self.data_dir, filename), os.path.join(self.data_dir, 'not_learning'))
                    print(f"Warning: Ignoring file \033[91m{filename}\033[0m because it does not have a supported file extension.")
                else:
                    print("learned:",filename)
                    

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
    return parser.parse_args()

def main():
    data_dir = './data'
    if not any(fname for fname in os.listdir(data_dir) if fname != '.gitignore' and not os.path.isdir(os.path.join(data_dir, fname))):
        print("No files to learn from in the 'data' directory. Exiting the program.")
        sys.exit()

    args = parse_arguments()
    if args.train:
        adding_data = AddingDataToGPT(retrain=True)
    else:
        adding_data = AddingDataToGPT()
    adding_data.run_conversation()

if __name__ == "__main__":
    main()