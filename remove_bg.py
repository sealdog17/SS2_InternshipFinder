from PIL import Image

def remove_white_bg(image_path):
    img = Image.open(image_path).convert("RGBA")
    data = img.getdata()
    new_data = []
    
    for r, g, b, a in data:
        # Check if the pixel is close to white
        # White is (255, 255, 255)
        if r > 230 and g > 230 and b > 230:
            # Make it fully transparent
            new_data.append((255, 255, 255, 0))
        else:
            # Keep original
            # For anti-aliased edges (values between 200 and 230), we could adjust alpha, 
            # but a hard threshold at 235 usually works reasonably well for simple logos
            if r > 200 and g > 200 and b > 200:
                avg = (r + g + b) / 3
                # Map avg from 200..230 to alpha 255..0
                alpha = int(255 * (230 - avg) / 30)
                alpha = max(0, min(255, alpha))
                new_data.append((r, g, b, alpha))
            else:
                new_data.append((r, g, b, a))
                
    img.putdata(new_data)
    img.save(image_path, "PNG")
    print("Background removed successfully!")

if __name__ == '__main__':
    remove_white_bg(r"c:\BTVN 2026 Spring\SS2\code hung sua\SS2_IF_hungsua\static\logo.png")
