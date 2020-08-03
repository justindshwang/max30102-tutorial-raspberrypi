import matplotlib.pyplot as plt
import math

L = 30
LS = 4
HIGH = 40
LOW = -40
DEV = 0.1

SAMPLE_RATE = 25
SAMPLE_INTERVAL_MS = 1000.0 / SAMPLE_RATE

plot_index = -1


def comp_ma(data, L):
    new_data = [0] * (len(data) - L + 1)
    for i in range(len(data) - L + 1):
        window = data[i : i + L]
        ave = sum(window) / L
        new_data[i] = ave
    return new_data

def comp_ac(data, ma):
    data_ac = [0] * len(ma)
    for i in range(len(ma)):
        data_ac[i] = data[i] - ma[i]
    return data_ac

def comp_derivative(data):
    new_data = [0] * (len(data) - 1)
    for i in range(len(data) - 1):
        new_data[i] = data[i + 1] - data[i]
    return new_data

def subplot(axs, data, title):
    global plot_index
    plot_index += 1
    axs[plot_index].plot(data)
    axs[plot_index].set_title(title)
    axs[plot_index].grid()

def get_peaks(data, high, low):
    def find_next_middle(data, pos):
        while pos < len(data):
            value = data[pos]
            if value < high and value > low:
                return pos
            pos += 1
        return None
   
    def find_next_high(data, pos):
        while pos < len(data):
            value = data[pos]
            if value >= high:
                return pos
            pos += 1
        return None

    def find_next_low(data, pos):
        while pos < len(data):
            value = data[pos]
            if value <= low:
                return pos
            pos += 1
        return None

    pos = find_next_middle(data, 0)
    if pos is None:
        print('find_next_middle error')
        return []

    peaks = []
    while pos < len(data):
        pos1 = find_next_high(data, pos)
        if pos1 is None:
            break
        pos2 = find_next_low(data, pos1)
        if pos2 is None:
            break
        tmp = data[pos1 : pos2]
        
        peak = pos1 + tmp.index(max(tmp))
        peaks.append(peak)
        pos = pos2
    return peaks        


def comp_RRs(data):
    RRs = [(data[i + 1] - data[i]) * SAMPLE_INTERVAL_MS for i in range(len(data) - 1)]
    return RRs

def comp_mRR(RRs):
    mRR = float(sum(RRs)) / len(RRs)
    return mRR

def comp_mHR(RRs):
    mHR = sum([60000.0 / rr for rr in RRs]) / len(RRs)
    return mHR

def comp_SDRR(RRs, mRR):
    SDRR = math.sqrt(sum([(rr - mRR) ** 2 for rr in RRs]) / (len(RRs) - 1))
    return SDRR

def comp_SDHR(RRs, mHR):
    SDHR = math.sqrt(sum([(60000.0 / rr - mHR) ** 2 for rr in RRs]) / (len(RRs) - 1))
    return SDHR

def comp_CRVV(mRR, SDRR):
    CRVV = SDRR * 100 / mRR
    return CRVV

def comp_RMSSD(RRs):
    RMSSD = math.sqrt(sum([(RRs[i + 1] - RRs[i]) ** 2 for i in range(len(RRs) - 1)])  / (len(RRs) - 1))    
    return RMSSD

def comp_pRR(RRs, thr):
    # return len([abs(RRs[i + 1] - RRs[i]) for i in range(len(RRs) - 1) if abs(RRs[i + 1] - RRs[i]) >= thr]) * 100 / (len(RRs) - 1)

    count = 0
    for i in range(len(RRs) - 1):
        diff = abs(RRs[i + 1] - RRs[i])
        if diff >= thr:
            count += 1
    pRR = float(count) / (len(RRs) - 1) * 100
    return pRR   

def comp_deviations(data, ave):
    return [abs(d - ave) / ave for d in data]

def check_deviations(data):
    return [d for d in data if d > DEV]



red = []

with open('myred.txt', 'r') as f:
    for line in f:
        red.append(int(line))

# Discard the first few points.
#red = red[10:100]
red = red[10:]

data = red

#compute moving average
ma = comp_ma(data, L)


#compute ac componet
data_ac = comp_ac(data, ma)


# Compute small window size average
small_ma = comp_ma(data_ac, LS)


# 1st derivative
data_1d = comp_derivative(small_ma)


# 2nd derivative
data_2d = comp_derivative(data_1d)

peaks = get_peaks(data_2d, HIGH, LOW)    

print(peaks)

RRs = comp_RRs(peaks)
print('RRs:', RRs)

mRR = comp_mRR(RRs)
print('mRR:', mRR)

mHR = comp_mHR(RRs)
print('mHR:', mHR)

SDRR = comp_SDRR(RRs, mRR)
print('SDRR:', SDRR)

SDHR = comp_SDHR(RRs, mHR)
print('SDHR:', SDHR)

CRVV = comp_CRVV(mRR, SDRR)
print('CRVV:', CRVV)

RMSSD = comp_RMSSD(RRs)
print('RMSSD:', RMSSD)

pRR20 = comp_pRR(RRs, 20)
print('pRR20:', pRR20)


pRR50 = comp_pRR(RRs, 50)
print('pRR50:', pRR50)


# Plot the figures.
#fig, axs = plt.subplots(2, sharex=True)
#fig.suptitle('PPG figures')

plt.plot(data_2d)
plt.xlabel('time')
plt.ylabel('change')
plt.title('data_2d')
plt.grid(True)
plt.savefig('flyaway.png')
plt.show()
