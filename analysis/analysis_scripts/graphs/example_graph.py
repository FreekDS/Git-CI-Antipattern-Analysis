import matplotlib.pyplot as plt
import json

from analyzer.utils import format_date

# TRAVIS --> GHA

with open('./sb1_example_antipatterns_before.json') as before_f:
    before = json.loads('\n'.join(before_f.readlines()))

with open('./sb1_example_antipatterns_after.json') as after_f:
    after = json.loads('\n'.join(after_f.readlines()))


data_before = before.get('slow_build', {}).get('additween').get('data')
data_after = after.get('slow_build', {}).get('Checks').get('data')

x = [i + 1 for i in range(len(data_before.keys()))]

dates1 = [format_date(d) for d in data_before.keys()]
dates2 = [format_date(d) for d in data_after.keys()]

vals = [v / 1000 for v in data_before.values()]
plt.plot(dates1, vals, marker='o', color='green', label='before (TravisCI)')
vals = [v / 1000 for v in data_after.values()]
plt.plot(dates2, vals, marker='o', color='blue', label='after (Github Actions)')
plt.gca().set_ylim([0, 60])
# plt.xticks(dates1 + dates2, rotation=90)
plt.xticks([0])
plt.legend()
plt.suptitle("Slow build")
plt.title("Comparison before and after for 'bhovhannes/additween'")
plt.ylabel("Average build time (s)")
# plt.xlabel("Start date of week")
plt.tight_layout()
plt.show()
print()


with open('./sb2_example_antipatterns_before.json') as before_f:
    before = json.loads('\n'.join(before_f.readlines()))

with open('./sb2_example_antipatterns_after.json') as after_f:
    after = json.loads('\n'.join(after_f.readlines()))


data_before2 = before.get('slow_build', {}).get('Build and publish image').get('data')
data_after2 = after.get('slow_build', {}).get('webssh2').get('data')

x = [i + 1 for i in range(len(data_before.keys()))]

dates1 = [format_date(d) for d in data_before2.keys()]
dates2 = [format_date(d) for d in data_after2.keys()]

vals = [v / 1000 for v in data_before2.values()]
plt.plot(range(1, 6), vals, marker='o', color='green', label='before (GitHub Actions)')
vals = [v / 1000 for v in data_after2.values()]
plt.plot(range(6, 10), vals, marker='o', color='blue', label='after (Travis CI)')
plt.gca().set_ylim([0, 300])
plt.xticks([0])
plt.legend()
plt.suptitle("Slow build")
plt.title("Comparison before and after for 'billchurch/WebSSH2'")
plt.ylabel("Average build time (s)")
# plt.xlabel("Start date of week")
plt.tight_layout()
plt.show()
print()

