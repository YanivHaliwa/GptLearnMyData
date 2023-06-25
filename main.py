#!/usr/bin/python3
import os
import openai
import os
import argparse
from llama_index import GPTVectorStoreIndex, Document, SimpleDirectoryReader,StorageContext,load_index_from_storage

openai.api_key=os.environ['OPENAI_API_KEY']
  
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
        if not os.listdir(self.data_dir):
            print("The data directory is empty. Please add data for the model to learn from.")
            exit()
        print("please wait...")
        documents = CustomDirectoryReader(self.data_dir).load_data()
        self.index = GPTVectorStoreIndex.from_documents(documents)
        self.index.storage_context.persist()

    def build_storage(self):
        if not os.listdir(self.data_dir):
            print("The data directory is empty. Please add data for the model to learn from.")
            exit()
        print("please wait...")
        documents = []
        for filename in os.listdir(self.data_dir):
            if filename == ".gitignore" or filename.startswith(".~lock"):
                 continue
            if not filename.endswith(".doc") and not filename.endswith(".docx") and not filename.endswith(".txt") and not filename.endswith(".html"):
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
    args = parse_arguments()
    if args.train:
        adding_data = AddingDataToGPT(retrain=True)
    else:
        adding_data = AddingDataToGPT()
    adding_data.run_conversation()

if __name__ == "__main__":
    main()