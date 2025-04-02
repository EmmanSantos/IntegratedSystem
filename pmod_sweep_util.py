from alive_progress import alive_bar
from math import floor

#   Searches for ITU Channel nearest to the desired frequency and calculates the necessary offset
#   Compares diffrence with previous channel and current channel in the list of channels; Since ch_list is sorted, if difference increases prev channel is the closest channel
def freq_search(f,ch_list_m):
    #initialize
    diff_prev = f-ch_list_m[0]
    diff_curr = 0
    nearest_ch = ch_list_m[0]
    ch_no = 96
    
    for ch_freq in ch_list_m[1:]:
        diff_curr = f-ch_freq
        if abs(diff_curr) >= abs(diff_prev):
            break
        ch_no=ch_no-1
        nearest_ch = ch_freq
        diff_prev = diff_curr

    return [ch_no,diff_prev,nearest_ch]

# converts wl in nm list to flist in m
def wl_to_f(wl_list):
    c=299792458
    f_list = []
    for wl in wl_list:
        f = round(c/(wl*1e-9)*1e-6)
        f_list.append(f)
    return f_list
    
#   generates list of settings that contain required channel number and Fine offset in MHZ
#   takes in wavelength in nm and stepsize in pm
#   [freq_at_ch_n,offset,ch_n]
def settings_list_gen(wlstart_nm:float,wlend_nm:float,wldelta_pm:float):
    c=299792458
    ch_list = [191500, 191550, 191600, 191650, 191700, 191750, 191800, 191850, 191900, 191950, 192000, 192050, 192100, 192150, 192200, 192250, 192300, 192350, 192400, 192450, 192500, 192550, 192600, 192650, 192700, 192750, 192800, 192850, 192900, 192950, 193000, 193050, 193100, 193150, 193200, 193250, 193300, 193350, 193400, 193450, 193500, 193550, 193600, 193650, 193700, 193750, 193800, 193850, 193900, 193950, 194000, 194050, 194100, 194150, 194200, 194250, 194300, 194350, 194400, 194450, 194500, 194550, 194600, 194650, 194700, 194750, 194800, 194850, 194900, 194950, 195000, 195050, 195100, 195150, 195200, 195250, 195300, 195350, 195400, 195450, 195500, 195550, 195600, 195650, 195700, 195750, 195800, 195850, 195900, 195950, 196000, 196050, 196100, 196150, 196200, 196250]
    ch_list_m = [196250000, 196200000, 196150000, 196100000, 196050000, 196000000, 195950000, 195900000, 195850000, 195800000, 195750000, 195700000, 195650000, 195600000, 195550000, 195500000, 195450000, 195400000, 195350000, 195300000, 195250000, 195200000, 195150000, 195100000, 195050000, 195000000, 194950000, 194900000, 194850000, 194800000, 194750000, 194700000, 194650000, 194600000, 194550000, 194500000, 194450000, 194400000, 194350000, 194300000, 194250000, 194200000, 194150000, 194100000, 194050000, 194000000, 193950000, 193900000, 193850000, 193800000, 193750000, 193700000, 193650000, 193600000, 193550000, 193500000, 193450000, 193400000, 193350000, 193300000, 193250000, 193200000, 193150000, 193100000, 193050000, 193000000, 192950000, 192900000, 192850000, 192800000, 192750000, 192700000, 192650000, 192600000, 192550000, 192500000, 192450000, 192400000, 192350000, 192300000, 192250000, 192200000, 192150000, 192100000, 192050000, 192000000, 191950000, 191900000, 191850000, 191800000, 191750000, 191700000, 191650000, 191600000, 191550000, 191500000]
    
    #build wl_list
    wllist_nm =[]
    w_nm = wlstart_nm
    while w_nm <= wlend_nm:
        wllist_nm.append(w_nm)
        w_nm = round(w_nm+wldelta_pm/1000,9) #prevent floating point arithmetic inaccuracy

    print(wllist_nm)

    flist_m = wl_to_f(wllist_nm)

    # print(flist_m)
    print("No. of Data Points",len(flist_m))

    settings_list = []
    i = 0
    for f in flist_m:
        settings = freq_search(f,ch_list_m)
        settings_list.append(settings)

        ftest = settings[2]+settings[1]
        # print(f,ftest,"Correct" if ftest == f else "Wrong"," Error vs wllist in nm: ",wllist_nm[i]-(c/(f*1e6))*1e9,settings)
        i=i+1
    
    # print(settings_list)

    return settings_list

def coarse_settings_list_gen(ch_start:int,ch_end:int):
    ch_list_rev = [191500000, 191550000, 191600000, 191650000, 191700000, 191750000, 191800000, 191850000, 191900000, 191950000, 192000000, 192050000, 192100000, 192150000, 192200000, 192250000, 192300000, 192350000, 192400000, 192450000, 192500000, 192550000, 192600000, 192650000, 192700000, 192750000, 192800000, 192850000, 192900000, 192950000, 193000000, 193050000, 193100000, 193150000, 193200000, 193250000, 193300000, 193350000, 193400000, 193450000, 193500000, 193550000, 193600000, 193650000, 193700000, 193750000, 193800000, 193850000, 193900000, 193950000, 194000000, 194050000, 194100000, 194150000, 194200000, 194250000, 194300000, 194350000, 194400000, 194450000, 194500000, 194550000, 194600000, 194650000, 194700000, 194750000, 194800000, 194850000, 194900000, 194950000, 195000000, 195050000, 195100000, 195150000, 195200000, 195250000, 195300000, 195350000, 195400000, 195450000, 195500000, 195550000, 195600000, 195650000, 195700000, 195750000, 195800000, 195850000, 195900000, 195950000, 196000000, 196050000, 196100000, 196150000, 196200000, 196250000] 
    c=299792458

    ch_sweep_list = []
    x = ch_start
    while x >= ch_end:
        ch_sweep_list.append(x)
        x = x-1

    print(ch_sweep_list)
    print("No. of Data Points",len(ch_sweep_list))

    settings_list = []
    i = 0
    for c in ch_sweep_list:
        settings = [c,0,ch_list_rev[c-1]]
        settings_list.append(settings)

        ftest = settings[2]+settings[1]
        # print(f,ftest,"Correct" if ftest == f else "Wrong"," Error vs wllist in nm: ",wllist_nm[i]-(c/(f*1e6))*1e9,settings)
        i=i+1
    
    # print(settings_list)

    return settings_list