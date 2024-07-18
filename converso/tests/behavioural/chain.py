# graph = FormAgentExecutor(tools=tools)

# # Define the evaluators to apply
# eval_config = smith.RunEvalConfig(
#     evaluators=[
#         "cot_qa"
#     ],
#     custom_evaluators=[],
#     eval_llm=chat_models.ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
# )

# client = langsmith.Client()
# chain_results = client.run_on_dataset(
#     dataset_name="Base",
#     llm_or_chain_factory=graph.app,
#     evaluation=eval_config,
#     project_name="test-internal-gunpowder-96",
#     concurrency_level=5,
#     verbose=True,
# )

# Replace with the chat model you want to test
# my_llm = ChatOpenAI(temperature=0)

# Define the evaluators to apply
