import openai
import os

def get_device_info(device_name):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Prompt for the OpenAI API to generate information
    prompt = f"Provide detailed information for the device named '{device_name}':\n\n" \
             f"1. Device name\n2. Voltage range (V)\n3. Current consumption (mA)\n4. Energy consumption (W) calculation\n5. Usage scenarios\n6. If the device is a development board:\n   - Power supply methods\n   - Supported protocol types\n   - Protocol coverage\n   - Product price (in USD)\n"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    # Input device name from the user
    device_name = input("Enter the device name: ")

    # Fetch and display device information
    device_info = get_device_info(device_name)
    print("\nDevice Information:")
    print(device_info)
