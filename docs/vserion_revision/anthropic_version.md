


### anthropic: v0.59.0
支持claude code 2.0.5，但不支持2.0.62
报错：API Error: 400 {"detail":"RuntimeError: Async function raised an error, please check the function. AsyncMessages.create() got an unexpected keyword argument 'context_management'\nRuntimeError: Async function raised an error, please check the function. AsyncMessages.create() got an unexpected 
    keyword argument 'context_management'"}
原因是：0.59.0版本的anthropic包不支持context_management参数
新的v0.75.0也不支持context_management参数，可能只能去掉context_management参数才能使用最新的claude code版本


