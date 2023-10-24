import os, sys
import hai

def request_model(prompt='hello', system_prompt=None):
    system_prompt = system_prompt if system_prompt else "Answering questions conversationally"

    result = hai.LLM.chat(
            # model='openai/gpt-3.5-turbo',
            model='hepai/vicuna-7B',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
                ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
                ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
            ],
            stream=True,
        )

    full_result = ""
    for i in result:
        full_result += i
        sys.stdout.write(i)
        sys.stdout.flush()
    print()
    return full_result


prompt = 'hello'
prompt2 = """
在以下天体事件观测日志["('S. Garrappa (Ruhr-Universitaet Bochum), J. Sinapius (DESY-Zeuthen) and S. Buson (Univ. of Wuerzburg) on behalf of the Fermi-LAT collaboration:We report an analysis of observations of the vicinity of the IC230405A\ufffd\ufffd high-energy neutrino event (GCN 33567) with all-sky survey data from the Large Area Telescope (LAT), on board the Fermi Gamma-ray Space Telescope. The IceCube event was detected on 2023-04-05 at 13:20:20.04 UT (T0) with J2000 position RA = 120.85 (+2.86, -4.98) deg, Decl. = +9.75 (+1.87, -2.17) deg (90% PSF containment).\ufffd\ufffd Seven cataloged gamma-ray (>100 MeV; The Fermi-LAT collaboration 2022, ApJS, 260, 53) sources are located within the 90% IC230405A\ufffd\ufffd localization region. Based on a preliminary analysis of the LAT data over a month and day timescale prior T0, these objects are not significantly detected at gamma rays.We searched for intermediate (days to years) timescale emission from a new gamma-ray transient source. Preliminary analysis indicates no significant (> 5 sigma) new excess emission (> 100 MeV) at the IC230405A best-fit position. Assuming a power-law spectrum (photon index = 2.0 fixed) for a point source at the IC230405A best-fit position, the >100 MeV flux upper limit (95% confidence) is < 1.8e-10 ph cm^-2 s^-1 for ~14-years (2008-08-04 to 2023-04-05 UTC), and < 9.4e-9 (<1.7e-7) ph cm^-2 s^-1 for a 1-month (1-day) integration time before T0.Since Fermi normally operates in an all-sky scanning mode, regular monitoring of this region will continue. For these observations the Fermi-LAT contact persons are S. Garrappa (simone.garrappa at ruhr-uni-bochum.de), J. Sinapius (jonas.sinapius at desy.de) and S. Buson (sara.buson at uni-wuerzburg.de).The Fermi-LAT is a pair conversion telescope designed to cover the energy band from 20 MeV to greater than 300 GeV. It is the product of an international collaboration between NASA and DOE in the U.S. and many scientific institut"]上执行命名实体识别，识别出上述日志描述中事件名称，观测该事件所使用的设备名称，事件的赤经，事件的赤纬和位置误差，未包含信息输出NONE。"
"""
answer = request_model(prompt=prompt2)

