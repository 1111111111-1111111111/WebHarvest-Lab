import pandas as pd

path = r'num.txt'

num = list(range(1,3554))
df = pd.DataFrame(num)
df.to_csv(path,index=False,header=False)