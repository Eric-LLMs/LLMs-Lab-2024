The steps of running the project is as follows: 

## Step 1: Set up .env
Configure the OPENAI_API_KEY in the .env file of the project with your own key.

```
OPENAI_API_KEY=sk-xxxx
```

## Step 2: Configuration:

Control whether certain packages use local (native) libraries during compilation and runtime.

Execute the following command:
```
export HNSWLIB_NO_NATIVE=1
```

## Step 3: Install Packages

Execute the following command:
```
pip install -r requirements.txt
```

## Step 4: Run

#### Run the main.py file

#### Then input your question in the interface:
🤖: How can I assist you?
👨: What is the sales amount for September? (need to input yourself)
 >>>>Round: 0<<<<

#### Sample Questions:
* What is the sales amount for September?
* Which product has the highest total sales?
* Help me identify suppliers with below-standard sales.
* Send an email to these two suppliers to notify them of this matter.
* Compare the sales performance of August and September and write a report.
