import matplotlib.pyplot as plt

def build_chart(prices):
    plt.plot(prices)
    plt.savefig("/data/chart.png")
