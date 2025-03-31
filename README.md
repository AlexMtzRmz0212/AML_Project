# Job Resume Chatbot

This is a chatbot that is aimed to help users generate job resumes given a job description. 

The chatbot is a RAG system using [LangChain](https://www.langchain.com/) and sending prompts to locally hosted LLM in [Ollama](https://ollama.com/).

The web application uses the [Django](https://www.djangoproject.com/) web framework as a base.

# Workflow Summary

A brief technical outline of what goes behind the scenes:

- The system builds embeddings of job resume dataset.
- User inputs a job description to build a resume out of.
- The system searches for relevant data as context from the stored embeddings.
- A prompt is sent to the locally hosted LLM that is built together from the information from the user and context data.
- The response is given to the user who can further edit the response or resend it with another prompt.
- If the user requires it, a PDF file of the response can be generated on demand.  

# Prerequisites

Required dependencies:

- [Django](https://pypi.org/project/Django/)
- [LangChain](https://pypi.org/project/langchain/)
- [LangChain Community](https://pypi.org/project/langchain-community/)

Besides those dependencies, you will also need to set up an LLM hosted in Ollama server.

# LLM in Ollama

For Linux, please refer to the following [Linux installation manual](https://github.com/ollama/ollama/blob/main/docs/linux.md)

For Windows, please refer to the following [Windows installation manual](https://github.com/ollama/ollama/blob/main/docs/windows.md)


# Run

To start the Django server, run from terminal:

```bash
python manage.py runserver
```

> :warning: `python manage.py migrate` may be needed if you run the server for the first time.

> :warning: Depending on your project architecture, changes in `rag.pipeline.py` may be needed for the model of the LLM, IP address and port of the Ollama host. The default configuration line in the file is `llm = OllamaLLM(model="llama3.2", base_url="http://127.0.0.1:11434/")`

### Package layout

If you wish to modify this repository, familiarity with Django will be helpful.
Here are some important files to note:

- `chatBot\views.py` contains the functions that handle incoming HTTP requests, process data, and return HTTP responses

- `chatBot\rag_pipeline.py` contains the functions that handle the RAG parts of the system 

- `chatBot\templates\chat\chat.html` is the web page that the user sees
