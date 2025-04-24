# Eurogate - Ai Hackathon 2025
AI Hackathon of Chefftreff Hamburg 2025 (24.4 - 25.4) - Submitition of our team for Challange 6 by Eurogate:

# The Task: 🧠 EUROGATE Hackathon Challenge: "Build the Smartest AI Agent!"

## Assignment:
Develop an intelligent AI agent that, based on a Retrieval-Augmented Generation (RAG) approach and Large Language Models (LLMs), is capable of answering complex user queries using provided documents (e.g., PDFs, texts, technical documentation). Various documents will be provided for the following use cases - choose one of the use cases:

- **The Infobox** is the internal employee portal at Eurogate. General information, news, and general documents are provided here.

- **driveMybox.io** is a digital platform for booking and carrying out truck container transports. In addition to general information (e.g., company presentation) and FAQs, database excerpts and external order documents are provided that could be used for further information on the status of the transport or a price inquiry via Quotation API.

- **Technical Services** offers engineering services and is responsible for the maintenance of facilities. Articles from the internal wiki, training materials, software instructions, and facility documents are provided.

## 🎯 Goal:
The AI agent should understand questions, extract relevant information from data sources, and deliver precise, context-related answers to support users in their daily work according to the chosen use case.

## 🛠️ What Your Agent Should Be Able To Do:
- Process questions (text or speech)
- Generate well-founded answers using an LLM (suitable for the respective use case)
- Indicate sources or references

## 🔧 Technology Tips:
Existing frameworks and LLMs should be used, e.g., LlamaIndex (https://www.llamaindex.ai) and OpenAI (an API key can be provided for this). Python is the preferred programming language.

## 💡 How You Implement This Is Up To You:
Whether through a chatbot interface, a web app, a CLI tool, or something completely different – the main thing is that the agent is intuitive to use and provides comprehensible answers.

## 🌟 Bonus Points For:
- An elegant, intuitive user interface
- Complex queries (e.g., order processing as PDF)
- Multimodal responses (e.g., combined text, table, or visualization answers)
- Transparent answer justification (e.g., through source citations or highlighting in the document)
- Voice input and voice output (Speech-to-Text + Text-to-Speech)

## 🔩 Material
Depending on the use case, the following materials are available:
- FAQs
- Database excerpts
- API descriptions
- Presentations
- Order documents


## Solution approach:

# Understanding the driveMyBox.io Challenge

I've analyzed the provided documents and understand that you're tackling the driveMyBox.io use case from the EUROGATE Hackathon Challenge. This challenge focuses on building an AI agent to process complex user queries using a RAG approach with LLMs. Let me provide you with a detailed breakdown of the task and requirements.

## Core Challenge Overview

You need to develop an intelligent AI agent that can:
1. Process user queries (text or speech)
2. Extract relevant information from provided documents
3. Generate accurate, context-specific responses
4. Support container logistics operations through driveMyBox.io

The system should automate data entry tasks that are currently manual, particularly for obtaining price quotations through an API.

## Document Analysis

From the documents provided, I can see you have:

1. **Challenge description** (Eurogate_challange6.pdf)
2. **Transport booking documents** (Amendment_EN250401098B.pdf, Cartage Advice documents)
3. **Container shipping details** (A2928880.pdf)
4. **Forum information** in JSON and XML formats about driveMyBox platform requirements

These documents contain structured information about container shipments, including:
- Container IDs and specifications
- Shipping routes and schedules
- Origin and destination information
- Weight and content details
- Transport booking references
- Pricing information

## System Architecture and Workflow

Here's a detailed breakdown of the proposed solution:


## Detailed System Components

### 1. Document Ingestion and Processing Pipeline

First, we need to process the provided documents to build our knowledge base:

### 2. Information Extraction System

The core of the system will be an intelligent extraction module that identifies and extracts key information from shipping documents:

### 3. Quotation API Integration Workflow

The specific workflow for price quotation generation:

## Key Tasks and Implementation Details

Based on my analysis, here's a detailed breakdown of the required tasks:

### 1. Data Extraction and Standardization

First, we need to build parsers for the different document types:

### 2. RAG System Implementation

Let's explore how the RAG system would process a query:

### 3. Price Quotation API Integration

Let's design the specific components for automating the price quotation process: