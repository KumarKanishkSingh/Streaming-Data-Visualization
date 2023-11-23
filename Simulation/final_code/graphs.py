import matplotlib.pyplot as plt
import numpy as np

# Data for 2 time steps
sizes_2_steps = [32, 64, 128, 256, 512]
create_times_2_steps = [0.5174643993377686, 0.5136420726776123, 0.4970741271972656, 0.46087646484375, 0.3102097511291504]
send_receive_times_2_steps = [4.965373277664185, 5.746278762817383, 5.109003782272339, 4.459750652313232, 5.598957777023315]
visualize_times_2_steps = [0.3275947570800781, 0.32512831687927246, 0.34769344329833984, 0.4363729953765869, 0.749290943145752]

# Data for 4 time steps
sizes_4_steps = [32, 64, 128, 256, 512]
create_times_4_steps = [1.4286072254180908, 1.5635621547698975, 1.0068316459655762, 1.1952035427093506, 1.198817253112793]
send_receive_times_4_steps = [5.0632569789886475, 2.222513437271118, 1.9276902675628662, 1.650115966796875, 1.9295039176940918]
visualize_times_4_steps = [0.6343815326690674, 0.6362855434417725, 0.6771645545959473, 0.8745546340942383, 1.4888179302215576]

# Adjusted figure size and subplot spacing
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
bar_width = 0.35
index = np.arange(len(sizes_2_steps))

# Plotting the grouped bar graph for 2 time steps
bar1_2_steps = axes[0].bar(index, create_times_2_steps, bar_width, label='Create and Simulate', color='blue')
bar2_2_steps = axes[0].bar(index, send_receive_times_2_steps, bar_width, bottom=create_times_2_steps, label='Send-Receive', color='orange')
bar3_2_steps = axes[0].bar(index, visualize_times_2_steps, bar_width, bottom=np.array(create_times_2_steps) + np.array(send_receive_times_2_steps),
                          label='Visualize', color='green')

axes[0].set_title('Performance Comparison for Different Array Sizes (2 Time Steps)')
axes[0].set_xlabel('Array Size')
axes[0].set_ylabel('Time (seconds)')
axes[0].set_xticks(index)
axes[0].set_xticklabels(sizes_2_steps)
axes[0].legend()

# Add labels at the top of each bar for 2 time steps
def add_labels_2_steps(bars):
    for bar in bars:
        height = bar.get_height()
        axes[0].annotate('{}'.format(round(height, 2)),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

add_labels_2_steps(bar1_2_steps)
add_labels_2_steps(bar2_2_steps)
add_labels_2_steps(bar3_2_steps)

# Plotting the grouped bar graph for 4 time steps
bar1_4_steps = axes[1].bar(index, create_times_4_steps, bar_width, label='Create and Simulate', color='blue')
bar2_4_steps = axes[1].bar(index, send_receive_times_4_steps, bar_width, bottom=create_times_4_steps, label='Send-Receive', color='orange')
bar3_4_steps = axes[1].bar(index, visualize_times_4_steps, bar_width, bottom=np.array(create_times_4_steps) + np.array(send_receive_times_4_steps),
                          label='Visualize', color='green')

axes[1].set_title('Performance Comparison for Different Array Sizes (4 Time Steps)')
axes[1].set_xlabel('Array Size')
axes[1].set_ylabel('Time (seconds)')
axes[1].set_xticks(index)
axes[1].set_xticklabels(sizes_4_steps)
axes[1].legend()

# Add labels at the top of each bar for 4 time steps
def add_labels_4_steps(bars):
    for bar in bars:
        height = bar.get_height()
        axes[1].annotate('{}'.format(round(height, 2)),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

add_labels_4_steps(bar1_4_steps)
add_labels_4_steps(bar2_4_steps)
add_labels_4_steps(bar3_4_steps)

# Adjust spacing between subplots
plt.tight_layout(w_pad=4.0)
plt.show()
