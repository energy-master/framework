import matplotlib.pyplot as plt
import json
import numpy as np
from scipy.interpolate import make_interp_spline

from scipy.interpolate import interp1d
data = None

with open("test_profile.json", "r") as f:
    data = json.load(f)
    


f_profile = []
e_profile = []

for f_frame in data['data']:
    print(f_frame)
    
    e_profile.append(f_frame['average_energy'] * -1)
    f_profile.append(f_frame['frequency'])

e_profile = np.array(e_profile)
f_profile = np.array(f_profile)

X_Y_Spline = make_interp_spline(f_profile, e_profile)
# Returns evenly spaced numbers
# over a specified interval.
X_ = np.linspace(f_profile.min(), f_profile.max(), 500)
Y_ = X_Y_Spline(X_)

# plt.plot( f_profile,e_profile , '-')
plt.plot( X_,Y_ , '-',color='green' )
plt.title('Brahma DM Power Spectrum Feed')
plt.xlabel('<f> (Hz)')
plt.ylabel('Power Spectrum (dB)')
plt.show()