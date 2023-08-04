# GPT Data Learning Application

This application is designed to train a GPT model to answer questions based on a set of data provided by the user. The application uses the GPT model from OpenAI and the Llama Index library to store and retrieve data.

as for now the data accepted is: 
Files with extensions -   .doc, .docx, .txt, .html, xls, xlsx, csv
also accepted is -  URL of website that contain the data.

## Prerequisites

Before running the application, you need to install the required Python libraries. You can do this by running the following command:

```
pip install -r requirements.txt
```

You also need to set your OpenAI API key as an environment variable. You can do this in Linux by running the following command:

```
export OPENAI_API_KEY='your-api-key'
```

Replace `'your-api-key'` with your actual OpenAI API key.

## Features

- Store and learn from a variety of data formats including .doc, .docx, .txt, and .html files.
- Ask the GPT model questions and receive answers based on the learned data.
- Retrain the model with new data as needed.
- The application can provide its own opinion based on the data provided.

## Getting Started

### Usage
 
```
git clone https://github.com/YanivHaliwa/GptLeanMyData.git
cd GptLeanMyData
```

To use the application, you need to provide data for the model to learn from. This data should be placed in the `data` directory. The application will ignore any files that do not have supported extensions as above.

Once the data is in place, you can run the application with the following command:

```
python gptLearn.py
```

During the execution of the application, you can ask the GPT model questions. The model will answer based on the data it has learned.

If you want to retrain the model with new data, you can use the `-t` or `--train` argument when running the application:

```
python gptLearn.py -t
```

To instruct the application to retrain the model during its execution, simply type `learn!` when prompted for a question.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request if you have something to add or improve.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
