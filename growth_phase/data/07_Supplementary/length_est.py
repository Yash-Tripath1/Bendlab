#%%
import pandas as pd

path = r"..\07_Supplementary\length_est_data.csv"
length_df = pd.read_csv(path, index_col = 0)

growth_speed = (length_df["length_finish"] - length_df["length_start"]) / length_df["dt"]

mean_growth_speed = growth_speed.mean()
std_growth_speed = growth_speed.std()
print(f"mean growth speed = {mean_growth_speed:.3f} ± {std_growth_speed:.3f} [mm/hour]")

overall_mean_s = length_df["length_start"].mean()
overall_std_s = length_df["length_start"].std()
overall_mean_f = length_df["length_finish"].mean()
overall_std_f = length_df["length_finish"].std()

print (f"mean Length at start = {overall_mean_s:.2f} ± {overall_std_s:.2f} [mm]")
print (f"mean Length at finish = {overall_mean_f:.2f} ± {overall_std_f:.2f} [mm]")
diff = overall_mean_f - overall_mean_s
print (f"mean Length difference = {diff:.2f} [mm]")
