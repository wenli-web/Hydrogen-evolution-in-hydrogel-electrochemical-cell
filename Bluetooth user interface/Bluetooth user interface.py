import pygame
from pygame.locals import *
import asyncio
import platform
from bleak import BleakClient, BleakScanner
import struct

# BLE address (replace with your device's address)
BLE_MAC_ADDR = "cf:cb:9c:e1:2c:5d"

# UUIDs for the BLE service and characteristics
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
COMMAND_CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
VOLTAGE_CHARACTERISTIC_UUID = "8628FE7C-A4E9-4056-91BD-FD6AA7817E39"

# Pygame initialization
pygame.init()
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Arduino Control Panel')
font = pygame.font.Font(None, 32)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)

# UI Components
up_button = pygame.Rect(50, 100, 100, 50)
down_button = pygame.Rect(250, 100, 100, 50)
input_box = pygame.Rect(50, 200, 300, 32)

# Global variables
voltage = 0 # in mV unit
input_text = ''
active_input = False
value = 0 # in uA unit
client = None  # Will store the BLE client instance

# Function to handle BLE notifications
def notification_handler(sender, data):
    global voltage
    read_voltage = struct.unpack('f', data)[0]     # unpack Bluetooth voltage
    real_voltage = 746.13 * read_voltage + 3.6399  # Apply voltage calibration
    voltage = real_voltage

# Function to send commands via BLE
async def send_command_ble(real_value):
    try:
        global client
        if client is not None:
            command_value = real_value/17.9  # Apply current calibration
            cmd_bytes = int(command_value).to_bytes(2, byteorder="little")
            await client.write_gatt_char(COMMAND_CHARACTERISTIC_UUID, cmd_bytes, response=True)
            print(f"Sent command: {real_value} uA")
    except Exception as e:
        print(f"Failed to send command: {e}")

# Async function to manage BLE connection
async def run_ble_client(address):
    global client
    device = await BleakScanner.find_device_by_address(address, timeout=20.0)
    if not device:
        raise Exception(f"Device with address {address} not found.")
    
    client = BleakClient(device)
    async with client:
        await client.start_notify(VOLTAGE_CHARACTERISTIC_UUID, notification_handler)
        print("BLE connected and receiving notifications")

        while True:
            await asyncio.sleep(1)  # Keep the connection alive

# Pygame loop to handle UI and BLE communication
async def run_pygame_loop():
    global input_text, active_input, value
    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(WHITE)
        
        # Draw buttons
        pygame.draw.rect(screen, GREEN, up_button)
        pygame.draw.rect(screen, GREEN, down_button)
        screen.blit(font.render("Up", True, BLACK), (up_button.x + 25, up_button.y + 10))
        screen.blit(font.render("Down", True, BLACK), (down_button.x + 25, down_button.y + 10))

        # Draw text input box with dynamic color
        box_color = LIGHT_BLUE if active_input else GRAY
        pygame.draw.rect(screen, box_color, input_box, 2)
        input_surface = font.render(input_text if input_text else 'Enter current in uA', True, BLACK)
        screen.blit(input_surface, (input_box.x + 10, input_box.y + 5))

        # Display voltage and current value
        voltage_text = font.render(f"Voltage: {voltage:.2f} mV", True, BLACK)
        screen.blit(voltage_text, (50, 50))
        value_text = font.render(f"Value: {value} uA", True, BLACK)
        screen.blit(value_text, (150, 160))

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == MOUSEBUTTONDOWN:
                if up_button.collidepoint(event.pos):
                    value += 1
                    await send_command_ble(value)  # Send incremented value via BLE
                elif down_button.collidepoint(event.pos):
                    value -= 1
                    await send_command_ble(value)  # Send decremented value via BLE
                elif input_box.collidepoint(event.pos):
                    active_input = True
                else:
                    active_input = False

            elif event.type == KEYDOWN and active_input:
                if event.key == K_RETURN:
                    try:
                        value = int(input_text)
                        await send_command_ble(value)  # Send the entered value via BLE
                        input_text = ''
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                elif event.key == K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)  # Allow other tasks to run

    pygame.quit()

# Main function to run both BLE and Pygame loops
async def main():
    address = BLE_MAC_ADDR if platform.system() != "Darwin" else "BLE_IDENTIFIER_FOR_MAC"
    ble_task = asyncio.create_task(run_ble_client(address))
    
    try:
        await run_pygame_loop()  # Run Pygame UI
    finally:
        ble_task.cancel()
        await ble_task

# If in an environment where an event loop is already running
async def start_main():
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    await main()

# This should be used if in an environment that doesn't allow asyncio.run() like Jupyter
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(start_main())
        else:
            asyncio.run(main())
    except RuntimeError as e:
        print(f"Runtime error: {e}")


