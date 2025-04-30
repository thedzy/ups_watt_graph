import itertools
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import mplcursors
import mplcursors
import pprint
import pywinusb.hid as hid
import pywinusb.hid as hid
import time
from datetime import datetime, timedelta
from enum import IntEnum


class HidPowerDeviceUsage(IntEnum):
    # Enumeration of HID usages for UPS and battery systems
    # https://github.com/networkupstools/nut/blob/master/drivers/libhid.c

    # Undefined = 0x00840000
    iName = 0x00840001
    PresentStatus = 0x00840002
    ChangedStatus = 0x00840003
    UPS = 0x00840004
    PowerSupply = 0x00840005
    # 0x00840006-0x0084000f	=>	Reserved 
    BatterySystem = 0x00840010
    BatterySystemID = 0x00840011
    Battery = 0x00840012
    BatteryID = 0x00840013
    Charger = 0x00840014
    ChargerID = 0x00840015
    PowerConverter = 0x00840016
    PowerConverterID = 0X00840017
    OutletSystem = 0x00840018
    OutletSystemID = 0x00840019
    Input = 0x0084001a
    InputID = 0x0084001b
    Output = 0x0084001c
    OutputID = 0x0084001d
    Flow = 0x0084001e
    FlowID = 0x0084001f
    Outlet = 0x00840020
    OutletID = 0x00840021
    Gang = 0x00840022
    GangID = 0x00840023
    PowerSummary = 0x00840024
    PowerSummaryID = 0x00840025
    # 0x00840026-0x0084002f	=>	Reserved 
    Voltage = 0x00840030
    Current = 0x00840031
    Frequency = 0x00840032
    ApparentPower = 0x00840033
    ActivePower = 0x00840034
    PercentLoad = 0x00840035
    Temperature = 0x00840036
    Humidity = 0x00840037
    BadCount = 0x00840038
    # 0x00840039-0x0084003f	=>	Reserved 
    ConfigVoltage = 0x00840040
    ConfigCurrent = 0x00840041
    ConfigFrequency = 0x00840042
    ConfigApparentPower = 0x00840043
    ConfigActivePower = 0x00840044
    ConfigPercentLoad = 0x00840045
    ConfigTemperature = 0x00840046
    ConfigHumidity = 0x00840047
    # 0x00840048-0x0084004f	=>	Reserved 
    SwitchOnControl = 0x00840050
    SwitchOffControl = 0x00840051
    ToggleControl = 0x00840052
    LowVoltageTransfer = 0x00840053
    HighVoltageTransfer = 0x00840054
    DelayBeforeReboot = 0x00840055
    DelayBeforeStartup = 0x00840056
    DelayBeforeShutdown = 0x00840057
    Test = 0x00840058
    ModuleReset = 0x00840059
    AudibleAlarmControl = 0x0084005a
    # 0x0084005b-0x0084005f	=>	Reserved 
    Present = 0x00840060
    Good = 0x00840061
    InternalFailure = 0x00840062
    VoltageOutOfRange1 = 0x00840063
    FrequencyOutOfRange = 0x00840064
    Overload = 0x00840065
    # Note: the correct spelling is "Overload", not "OverLoad",
    #  according to the official specification, "Universal Serial
    #  Bus Usage Tables for HID Power Devices", Release 1.0,
    #  November 1, 1997
    OverCharged = 0x00840066
    OverTemperature = 0x00840067
    ShutdownRequested = 0x00840068
    ShutdownImminent = 0x00840069
    SwitchOn_Off = 0x0084006b
    Switchable = 0x0084006c
    Used = 0x0084006d
    Boost = 0x0084006e
    Buck = 0x0084006f
    Initialized = 0x00840070
    Tested = 0x00840071
    AwaitingPower = 0x00840072
    CommunicationLost = 0x00840073
    # 0x00840074-0x008400fc	=>	Reserved 
    iManufacturer = 0x008400fd
    iProduct = 0x008400fe
    iSerialNumber = 0x008400ff

    # Battery System Page 
    # Undefined = 0x00850000
    SMBBatteryMode = 0x00850001
    SMBBatteryStatus = 0x00850002
    SMBAlarmWarning = 0x00850003
    SMBChargerMode = 0x00850004
    SMBChargerStatus = 0x00850005
    SMBChargerSpecInfo = 0x00850006
    SMBSelectorState = 0x00850007
    SMBSelectorPresets = 0x00850008
    SMBSelectorInfo = 0x00850009
    # 0x0085000A-0x0085000f	=>	Reserved 
    OptionalMfgFunction1 = 0x00850010
    OptionalMfgFunction2 = 0x00850011
    OptionalMfgFunction3 = 0x00850012
    OptionalMfgFunction4 = 0x00850013
    OptionalMfgFunction5 = 0x00850014
    ConnectionToSMBus = 0x00850015
    OutputConnection = 0x00850016
    ChargerConnection = 0x00850017
    BatteryInsertion = 0x00850018
    Usenext = 0x00850019
    OKToUse = 0x0085001a
    BatterySupported = 0x0085001b
    SelectorRevision = 0x0085001c
    ChargingIndicator = 0x0085001d
    # 0x0085001e-0x00850027	=>	Reserved 
    ManufacturerAccess = 0x00850028
    RemainingCapacityLimit = 0x00850029
    RemainingTimeLimit = 0x0085002a
    AtRate = 0x0085002b
    CapacityMode = 0x0085002c
    BroadcastToCharger = 0x0085002d
    PrimaryBattery = 0x0085002e
    ChargeController = 0x0085002f
    # 0x00850030-0x0085003f	=>	Reserved 
    TerminateCharge = 0x00850040
    TerminateDischarge = 0x00850041
    BelowRemainingCapacityLimit = 0x00850042
    RemainingTimeLimitExpired = 0x00850043
    Charging = 0x00850044
    Discharging = 0x00850045
    FullyCharged = 0x00850046
    FullyDischarged = 0x00850047
    ConditioningFlag = 0x00850048
    AtRateOK = 0x00850049
    SMBErrorCode = 0x0085004a
    NeedReplacement = 0x0085004b
    # 0x0085004c-0x0085005f	=>	Reserved 
    AtRateTimeToFull = 0x00850060
    AtRateTimeToEmpty = 0x00850061
    AverageCurrent = 0x00850062
    Maxerror = 0x00850063
    RelativeStateOfCharge = 0x00850064
    AbsoluteStateOfCharge = 0x00850065
    RemainingCapacity = 0x00850066
    FullChargeCapacity = 0x00850067
    RunTimeToEmpty = 0x00850068
    AverageTimeToEmpty = 0x00850069
    AverageTimeToFull = 0x0085006a
    CycleCount = 0x0085006b
    # 0x0085006c-0x0085007f	=>	Reserved 
    BattPackModelLevel = 0x00850080
    InternalChargeController = 0x00850081
    PrimaryBatterySupport = 0x00850082
    DesignCapacity = 0x00850083
    SpecificationInfo = 0x00850084
    ManufacturerDate = 0x00850085
    SerialNumber = 0x00850086
    iManufacturerName = 0x00850087
    iDevicename = 0x00850088
    iDeviceChemistry = 0x00850089
    ManufacturerData = 0x0085008a
    Rechargeable = 0x0085008b
    WarningCapacityLimit = 0x0085008c
    CapacityGranularity1 = 0x0085008d
    CapacityGranularity2 = 0x0085008e
    iOEMInformation = 0x0085008f
    # 0x00850090-0x008500bf	=>	Reserved 
    InhibitCharge = 0x008500c0
    EnablePolling = 0x008500c1
    ResetToZero = 0x008500c2
    # 0x008500c3-0x008500cf	=>	Reserved 
    ACPresent = 0x008500d0
    BatteryPresent = 0x008500d1
    PowerFail = 0x008500d2
    AlarmInhibited = 0x008500d3
    ThermistorUnderRange = 0x008500d4
    ThermistorHot = 0x008500d5
    ThermistorCold = 0x008500d6
    ThermistorOverRange = 0x008500d7
    VoltageOutOfRange2 = 0x008500d8
    CurrentOutOfRange = 0x008500d9
    CurrentNotRegulated = 0x008500da
    VoltageNotRegulated = 0x008500db
    MasterMode = 0x008500dc
    # 0x008500dd-0x008500ef	=>	Reserved 
    ChargerSelectorSupport = 0x008500f0
    ChargerSpec = 0x008500f1
    Level2 = 0x008500f2
    Level3 = 0x008500f3


def main():
    # https://github.com/networkupstools/nut/blob/master/drivers/apc-hid.c
    ups = find_ups_device(vendor_id=0x051D, product_id=0x0002)
    ups.open()
    if not ups:
        print('No APC UPS found.')
    else:
        print('Connected to:', ups.vendor_name)
        config_active_power = get_report(ups, HidPowerDeviceUsage.ConfigActivePower)
        total_watts = (config_active_power[2] << 8) + config_active_power[1]
        print(f'Total Power Output {total_watts}w')

    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)
    ax.set_xlabel('Samples (seconds)')
    ax.set_ylabel('Watts')
    ax.set_title('Live UPS Power Draw')
    fig.canvas.manager.set_window_title('Live UPS Monitor')
    ax.grid()
    lines = [line]
    cursor = mplcursors.cursor(lines, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        index = int(round(sel.target[0]))
        if 0 <= index < len(timestamps):
            time_label = timestamps[index]
            value = sel.target[1]
            sel.annotation.set_text(f'{time_label} - {value:.1f}W')

    ani = animation.FuncAnimation(fig, animate, fargs=(ups, ax, line), interval=1000)

    plt.tight_layout()
    plt.show()

    ups.close()


def get_current_watts(device: hid.HidDevice) -> float:
    """
    Calculates the current power draw in watts using percent load and configured active power.
    :param device: The HID device to query for data
    :return: The calculated power draw in watts as a float, or 0 if unavailable
    """
    try:
        percentage_load = get_report(device, HidPowerDeviceUsage.PercentLoad)[1]
        config_active_power = get_report(device, HidPowerDeviceUsage.ConfigActivePower)
        total_watts = (config_active_power[2] << 8) + config_active_power[1]
        watts = total_watts * percentage_load / 100
    except:
        return 0
    return watts


def find_ups_device(vendor_id: int, product_id: int) -> Optional[hid.HidDevice]:
    """
    Finds and returns the UPS HID device matching the specified vendor and product ID.
    :param vendor_id: The vendor ID of the UPS device (e.g. 0x051D for APC)
    :param product_id: The product ID of the UPS device (e.g. 0x0002 for Back-UPS)
    :return: An instance of pywinusb.hid.HidDevice if found, otherwise None
    """
    filter = hid.HidDeviceFilter(vendor_id=vendor_id, product_id=product_id)
    devices = filter.get_devices()
    return devices[0]


def get_report(device: hid.HidDevice, usage: int, verbose: bool = False) -> Optional[List[int]]:
    """
    Fetches a HID feature report for a given usage from the UPS device.
    :param device: The HID device object (instance of pywinusb.hid.HidDevice)
    :param usage: An integer representing the full HID usage (0xUUUUIIII), where
                  the upper 16 bits are the usage page and the lower 16 bits are the usage ID
    :param verbose: If True, prints diagnostic messages when no report is found
    :return: A list of raw bytes from the HID report, or None if unavailable
    """
    usage_page = (usage >> 16) & 0xFFFF
    usage_id = usage & 0xFFFF
    feature = device.find_feature_reports(usage_page=usage_page, usage_id=usage_id)
    if not feature:
        if verbose:
            print(f'No report for usage_page={hex(usage_page)}, usage_id={hex(usage_id)}')
        return None
    feature_data = feature.pop()
    return feature_data.get()


def animate(frame: int, device: hid.HidDevice, ax: Any, line: Any) -> None:
    """
    Updates the matplotlib line graph with the latest UPS power data.
    :param frame: Frame index passed by FuncAnimation (unused here, but required by signature)
    :param device: The pywinusb HID device object representing the UPS
    :param ax: The matplotlib Axes object used for plotting
    :param line: The matplotlib Line2D object representing the power draw curve
    :return: None
    """
    watts = get_current_watts(device)
    if watts is not None:
        timestamps.append(time.strftime('%H:%M:%S'))
        watts_list.append(watts)

        if len(timestamps) > data_points:
            timestamps.pop(0)
            watts_list.pop(0)

        line.set_data(range(len(watts_list)), watts_list)
        ax.set_xlim(0, len(watts_list))
        ax.set_ylim(0, max(watts_list) * 1.2 if watts_list else 100)


if __name__ == '__main__':
    data_points = 600
    timestamps = []
    for seconds in range(data_points):
        timestamp = datetime.now() - timedelta(seconds=seconds)
        timestamps.insert(0, timestamp.strftime('%H:%M:%S'))
    watts_list = [0] * data_points
    main()
