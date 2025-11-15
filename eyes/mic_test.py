import sounddevice as sd
import numpy as np
import time

print("=" * 60)
print("MICROPHONE TEST")
print("=" * 60)

# List available audio devices
print("\nAvailable Audio Devices:")
print("-" * 60)
devices = sd.query_devices()
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        default = " (DEFAULT)" if i == sd.default.device[0] else ""
        print(f"{i}: {device['name']}{default}")
        print(f"   Input Channels: {device['max_input_channels']}")
        print(f"   Sample Rate: {device['default_samplerate']}")
        print()

# Get default input device
default_device = sd.query_devices(kind='input')
print(f"Using Microphone: {default_device['name']}")
print("-" * 60)

# Test recording
print("\nTesting microphone input...")
print("Make some noise (talk, knock, clap)...")
print()

sample_rate = 44100
duration = 5  # seconds
max_volume = 0

def audio_callback(indata, frames, time_info, status):
    global max_volume
    if status:
        print(f"Status: {status}")
    
    volume = np.sqrt(np.mean(indata**2))
    max_volume = max(max_volume, volume)
    
    # Visual bar
    bar_length = int(volume * 100)
    bar = "█" * min(bar_length, 50)
    print(f"\rVolume: {bar:<50} {volume:.4f}", end="", flush=True)

print("Recording for 5 seconds...")
print()

try:
    with sd.InputStream(
        channels=1,
        samplerate=sample_rate,
        callback=audio_callback
    ):
        time.sleep(duration)
    
    print("\n")
    print("-" * 60)
    print(f"SUCCESS! Microphone is working!")
    print(f"   Max volume detected: {max_volume:.4f}")
    print()
    
    if max_volume < 0.01:
        print("WARNING: Volume very low!")
        print("   - Check if microphone is muted")
        print("   - Check microphone permissions")
        print("   - Try speaking louder or closer to mic")
    elif max_volume < 0.05:
        print("WARNING: Volume is low but detectable")
        print("   - Try speaking louder")
        print("   - Check microphone sensitivity settings")
    else:
        print("SUCCESS! Volume levels look good!")
        print("   - Microphone is working properly")
    
    print()
    print("Suggested thresholds for knock detection:")
    print(f"   - Volume threshold: {max_volume * 0.5:.3f} to {max_volume * 0.7:.3f}")
    print(f"   - Spike threshold: {max_volume * 0.1:.3f} to {max_volume * 0.2:.3f}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    print("\nPossible issues:")
    print("   - No microphone connected")
    print("   - Microphone permissions denied")
    print("   - Another application is using the microphone")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)

