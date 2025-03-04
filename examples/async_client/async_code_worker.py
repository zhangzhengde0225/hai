import os, logging
import asyncio
from hepai import HRModel, ChatCompletionChunk

logger = logging.getLogger()
logging.basicConfig(level="DEBUG")
logging.getLogger().setLevel("DEBUG")

# 1. 在本机或者远程服务器配置代码执行器
# 下载链接见drsai/modules/components/actuators/code_woker_v2.md
# 运行方式见https://code.ihep.ac.cn/xuliang/drsai-code-worker-v2

# 2.配置访问代码执行器的必要参数
api_key = os.environ.get('HEPAI_API_KEY')
config_list = [
    {
    "model": "openai/gpt-4o-mini",
    "base_url": "https://aiapi.ihep.ac.cn/v1",
    "api_key": api_key,
    "api_type": "hepai",
    "proxy": None,
    "stream": True,
    },
    {
    "model": "openai/gpt-4o",
    "base_url": "https://aiapi.ihep.ac.cn/v1",
    "api_key": api_key,
    "api_type": "hepai",
    "proxy": None,
    "stream": True,
    },
    {
    "model": "xiwu_v2",
    "base_url": "https://aiapi.ihep.ac.cn/v1",
    "api_key": api_key,
    "api_type": "hepai",
    "proxy": None,
    "stream": True,
    },
    ]

llm_config = {
    "config_list": config_list,
    "temperature": 0,
    "timeout": 120,
    "top_p": 1,
}


# 3.发送代码消息测试代码执行器
query_text="""
Here’s an example of a simple CMake project that uses CERN ROOT to draw a histogram.

CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.10)
project(ROOTHistogram)

# Find the ROOT package
find_package(ROOT REQUIRED)

# Include ROOT headers
include(${ROOT_USE_FILE})

# Create an executable
add_executable(histogram histogram.cpp)

# Link ROOT libraries
target_link_libraries(histogram ${ROOT_LIBRARIES})
```

histogram.cpp
```cpp
#include "TH1F.h"
#include "TCanvas.h"
#include "TRandom.h"
#include <iostream>

int main() {
    // Create a histogram with 100 bins between 0 and 100
    TH1F *hist = new TH1F("hist", "Example Histogram", 100, 0, 100);

    // Fill the histogram with random data
    for (int i = 0; i < 10000; ++i) {
        hist->Fill(gRandom->Uniform(0, 100));
    }

    // Create a canvas and draw the histogram
    TCanvas *canvas = new TCanvas("canvas", "Histogram Canvas", 800, 600);
    hist->Draw();

    // Save the canvas as a PNG file
    canvas->SaveAs("histogram.png");

    // Cleanup
    delete hist;
    delete canvas;

    return 0;
}
```

Add X,Y label:

```cpp
histogram.cpp
<<<<<<< ORIGINAL
    hist->Draw();
=======
    hist->GetXaxis()->SetTitle("X-axis Title");
    hist->GetYaxis()->SetTitle("Y-axis Title");
    hist->Draw();
>>>>>>> UPDATED
```

Steps to Build and Run
	1.	Create a project directory and save the CMakeLists.txt and histogram.cpp files inside it.
	2.	Create a build directory inside the project directory:

```bash
mkdir -p build && cd build
```

	3.	Configure the project with CMake:

```bash
cmake ..
```

	4.	Build the project:

```bash
make
```

	5.	Run the executable to generate the histogram:

```bash
./histogram
```

Worker, please run the code.
"""

messages = [{"role":"user", "content":query_text}]
worker_config={"job_timeout": 30}

async def main():
    model = await HRModel.async_connect(
        name="hepai/code-worker-v2-aiboss",
        # base_url="http://localhost:44001/apiv2"
        # base_url="http://localhost:42899/apiv2",
        api_key=os.environ.get('HEPAI_API_KEY2'),
        base_url="https://aiapi001.ihep.ac.cn/apiv2"
    )

    rst = await model.interface(messages = messages, worker_config=worker_config, stream=True)

    async for chunk in rst:
        chunk: ChatCompletionChunk = chunk
        x = chunk.choices[0].delta.content
        if x:
            print(x, end="", flush=True)

asyncio.run(main())