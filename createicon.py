from PIL import Image

ico = Image.open("BillCore.ico")

print("Available icon sizes inside ICO:")
print(ico.info.get("sizes"))