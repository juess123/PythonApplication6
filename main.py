
from converters.SvgToDxf import svgTodxf
import time    
if __name__ == "__main__":
    start = time.perf_counter()
    svgTodxf()
    end = time.perf_counter()
    print(f"svgTodxf() 耗时: {end - start:.6f} 秒")
