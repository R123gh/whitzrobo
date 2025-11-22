import streamlit as st
import pandas as pd
import json
import os
from PIL import Image, ImageDraw, ImageFont
import plotly.express as px
from datetime import datetime
import time

# Initialize session state variables
if 'user' not in st.session_state:
    st.session_state.user = None
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"
if 'view_product' not in st.session_state:
    st.session_state.view_product = None
if 'checkout_total' not in st.session_state:
    st.session_state.checkout_total = 0
if 'show_order_success' not in st.session_state:
    st.session_state.show_order_success = False

# Page configuration
st.set_page_config(
    page_title="Whizrobotics Store",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with modern styling and animations
st.markdown("""
<style>
    /* Modern CSS with animations */
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        animation: fadeIn 1s ease-in;
    }
    
    .product-card {
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        margin: 0.5rem;
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        height: 100%;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .product-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .product-card:hover::before {
        left: 100%;
    }
    
    .category-card {
        text-align: center;
        padding: 1.5rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    .category-card:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
    }
    
    .price-tag {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff6b6b;
        background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .stButton button {
        width: 100%;
        border-radius: 10px;
        border: none;
        padding: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Animation keyframes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
        40% {transform: translateY(-10px);}
        60% {transform: translateY(-5px);}
    }
    
    .animated-card {
        animation: fadeIn 0.6s ease-out;
    }
    
    .bounce-animation {
        animation: bounce 1s;
    }
    
    /* Modern scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    /* Grid improvements */
    .css-1r6slb0 {
        gap: 1rem;
    }
    
    /* Hero section styling */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: slideIn 0.8s ease-out;
    }
    
    /* Badge for stock status */
    .stock-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .in-stock {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
    }
    
    .low-stock {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
    }
    
    .out-of-stock {
        background: linear-gradient(135deg, #f44336, #d32f2f);
        color: white;
    }
    
    /* Floating action button */
    .floating-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        animation: bounce 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

class RoboticsStore:
    def __init__(self):
        self.products = pd.DataFrame()
        self.categories = []
        self.load_data()
    
    def _darken_color(self, color, factor=0.8):
        """Darken a hex color by a factor - MOVED TO TOP OF CLASS"""
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            dark_rgb = tuple(int(c * factor) for c in rgb)
            return f"#{dark_rgb[0]:02x}{dark_rgb[1]:02x}{dark_rgb[2]:02x}"
        except:
            return color  # Return original color if processing fails
        
    def load_data(self):
        """Load products and orders data"""
        try:
            # Check if data file exists, if not create it
            if not os.path.exists('data/products.json'):
                st.warning("Data files not found. Creating sample data...")
                self.create_sample_data()
            
            with open('data/products.json', 'r') as f:
                data = json.load(f)
                self.products = pd.DataFrame(data['products'])
                self.categories = data['categories']
                
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.info("Creating sample data...")
            self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample data if files don't exist"""
        try:
            os.makedirs('data', exist_ok=True)
            os.makedirs('images', exist_ok=True)
            
            sample_data = {
                "products": [
                    {
                        "id": 1, "name": "Arduino Uno R3", "category": "Development Boards", 
                        "price": 450, "description": "Microcontroller board with ATmega328P - perfect for beginners and advanced users alike.",
                        "image": "images/arduino-uno.jpg", "stock": 25, "rating": 4.5,
                        "features": ["ATmega328P", "14 Digital I/O", "6 Analog Inputs", "USB Connection"]
                    },
                    {
                        "id": 2, "name": "Ultrasonic Sensor", "category": "Sensors", 
                        "price": 120, "description": "HC-SR04 distance measurement sensor with high accuracy and stable performance.",
                        "image": "images/sensor-ultrasonic.jpg", "stock": 50, "rating": 4.3,
                        "features": ["5V Operation", "2cm-450cm Range", "High Accuracy", "Easy to Use"]
                    },
                    {
                        "id": 3, "name": "DC Gear Motor", "category": "Motors", 
                        "price": 280, "description": "300 RPM high torque motor perfect for robotics and automation projects.",
                        "image": "images/motor-dc.jpg", "stock": 30, "rating": 4.4,
                        "features": ["300 RPM", "3-12V Operation", "High Torque", "Long Lifespan"]
                    },
                    {
                        "id": 4, "name": "Robot Wheels Set", "category": "Wheels", 
                        "price": 180, "description": "Set of 4 premium wheels for robotics with excellent grip and durability.",
                        "image": "images/wheels.jpg", "stock": 40, "rating": 4.2,
                        "features": ["65mm Diameter", "Set of 4", "Rubber Tires", "Smooth Movement"]
                    },
                    {
                        "id": 5, "name": "Camera Module", "category": "Cameras", 
                        "price": 850, "description": "5MP high-quality Raspberry Pi camera module with 1080p video recording.",
                        "image": "images/camera-module.jpg", "stock": 15, "rating": 4.6,
                        "features": ["5MP", "1080p Video", "Raspberry Pi Compatible", "Easy Setup"]
                    },
                    {
                        "id": 6, "name": "Li-ion Battery", "category": "Batteries", 
                        "price": 220, "description": "18650 2600mAh high-capacity rechargeable battery with protection circuit.",
                        "image": "images/battery-liion.jpg", "stock": 60, "rating": 4.1,
                        "features": ["2600mAh", "3.7V", "Rechargeable", "Long Cycle Life"]
                    },
                    {
                        "id": 7, "name": "Jumper Wires", "category": "Wires & Components", 
                        "price": 150, "description": "Premium set of 120pcs jumper wires in multiple types and lengths.",
                        "image": "images/wires-jumper.jpg", "stock": 75, "rating": 4.7,
                        "features": ["120pcs Set", "Multiple Types", "Different Lengths", "High Quality"]
                    },
                    {
                        "id": 8, "name": "Robotics Starter Kit", "category": "Project Kits", 
                        "price": 2500, "description": "Complete robotics starter kit with everything you need to begin your robotics journey.",
                        "image": "images/project-kit.jpg", "stock": 10, "rating": 4.8,
                        "features": ["Complete Kit", "Arduino Included", "Step-by-step Guide", "20+ Projects"]
                    }
                ],
                "categories": [
                    {"id": 1, "name": "Development Boards", "icon": "💻", "color": "#FF6B6B"},
                    {"id": 2, "name": "Sensors", "icon": "📡", "color": "#4ECDC4"},
                    {"id": 3, "name": "Motors", "icon": "⚙️", "color": "#45B7D1"},
                    {"id": 4, "name": "Wheels", "icon": "🛞", "color": "#96CEB4"},
                    {"id": 5, "name": "Cameras", "icon": "📷", "color": "#FFEAA7"},
                    {"id": 6, "name": "Batteries", "icon": "🔋", "color": "#DDA0DD"},
                    {"id": 7, "name": "Wires & Components", "icon": "🔌", "color": "#98D8C8"},
                    {"id": 8, "name": "Project Kits", "icon": "🧩", "color": "#F7DC6F"}
                ]
            }
            
            with open('data/products.json', 'w') as f:
                json.dump(sample_data, f, indent=2)
            
            # Create simple placeholder images
            self.create_placeholder_images()
            
            # Reload data
            with open('data/products.json', 'r') as f:
                data = json.load(f)
                self.products = pd.DataFrame(data['products'])
                self.categories = data['categories']
                
        except Exception as e:
            st.error(f"Failed to create sample data: {e}")
    
    def create_placeholder_images(self):
        """Create simple placeholder images"""
        try:
            for product in self.products.to_dict('records'):
                filename = product['image']
                # Different colors for different categories
                colors = {
                    "Development Boards": "#1E90FF",
                    "Sensors": "#32CD32", 
                    "Motors": "#FF6347",
                    "Wheels": "#FFD700",
                    "Cameras": "#8A2BE2",
                    "Batteries": "#DC143C",
                    "Wires & Components": "#20B2AA",
                    "Project Kits": "#FF69B4"
                }
                color = colors.get(product['category'], "#1E90FF")
                text = product['name']
                
                # Create a simple image
                img = Image.new('RGB', (400, 300), color=color)
                draw = ImageDraw.Draw(img)
                
                # Try to use a font
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                # Add text
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                x = (400 - text_width) // 2
                y = 150
                
                draw.text((x, y), text, fill='white', font=font)
                img.save(filename, 'JPEG')
                
        except Exception as e:
            print(f"Note: Could not create images: {e}")
    
    def create_fallback_image(self, text="Product Image", width=400, height=300):
        """Create a fallback image with text"""
        img = Image.new('RGB', (width, height), color=(73, 109, 137))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font)
        return img
    
    def load_product_image(self, image_path):
        """Load product image with fallback handling"""
        try:
            if os.path.exists(image_path):
                return Image.open(image_path)
            else:
                return self.create_fallback_image("Product Image")
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return self.create_fallback_image("Image Not Available")
    
    def sidebar_navigation(self):
        """Create sidebar navigation"""
        with st.sidebar:
            if st.session_state.user:
                st.markdown(f"<div style='animation: fadeIn 0.8s;'><h2>👋 Welcome, {st.session_state.user['name']}!</h2></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='animation: fadeIn 0.8s;'><h2>🤖 Whizrobotics Store</h2></div>", unsafe_allow_html=True)
            
            st.divider()
            
            # Navigation buttons
            pages = [
                ("🏠 ", "Home"),
                ("📦 ", "Products"), 
                ("🛒 ", "Cart"),
                ("📋", "Orders"),
                ("📊 ", "Analytics")
            ]
            
            for icon, page in pages:
                if st.button(f"{icon} {page}", key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    if 'view_product' in st.session_state:
                        del st.session_state.view_product
                    st.rerun()
            
            st.divider()
            
            # Cart summary with animation
            cart_count = len(st.session_state.cart)
            if cart_count > 0:
                st.markdown(f"<div class='bounce-animation'>🛒 Cart Items: <strong>{cart_count}</strong></div>", unsafe_allow_html=True)
            else:
                st.write(f"🛒 Cart Items: **{cart_count}**")
            
            if st.session_state.user:
                if st.button("🚪 Logout", use_container_width=True):
                    st.session_state.user = None
                    st.session_state.cart = []
                    st.session_state.current_page = "Home"
                    st.rerun()
    
    def login_page(self):
        """User login/signup page"""
        st.markdown('<div class="main-header">🤖 Whizrobotics Store</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="animated-card">', unsafe_allow_html=True)
            st.subheader("🔐 Login")
            with st.form("login_form"):
                email = st.text_input("📧 Email", value="user@example.com")
                password = st.text_input("🔒 Password", type="password", value="password")
                login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
                
                if login_btn:
                    if email and password:
                        st.session_state.user = {
                            "email": email,
                            "name": email.split('@')[0].title()
                        }
                        st.success(f"🎉 Welcome back, {st.session_state.user['name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Please enter email and password!")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="animated-card">', unsafe_allow_html=True)
            st.subheader("📝 Sign Up")
            with st.form("signup_form"):
                new_email = st.text_input("📧 New Email", value="newuser@example.com")
                new_name = st.text_input("👤 Full Name", value="New User")
                new_password = st.text_input("🔒 New Password", type="password", value="password")
                confirm_password = st.text_input("✅ Confirm Password", type="password", value="password")
                signup_btn = st.form_submit_button("✨ Create Account", use_container_width=True)
                
                if signup_btn:
                    if new_password == confirm_password:
                        if new_email and new_name:
                            st.session_state.user = {
                                "email": new_email,
                                "name": new_name
                            }
                            st.success(f"🎉 Account created! Welcome, {new_name}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Please fill all fields!")
                    else:
                        st.error("❌ Passwords don't match!")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Demo credentials
            st.markdown("""
            <div class="animated-card" style="padding: 1rem; border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <h4>🎯 Demo Credentials</h4>
                <p><strong>Email:</strong> user@example.com</p>
                <p><strong>Password:</strong> password</p>
            </div>
            """, unsafe_allow_html=True)
    
    def home_page(self):
        """Home page with categories and featured products"""
        st.markdown('<div class="main-header">🤖 Whizrobotics Store</div>', unsafe_allow_html=True)
        
        # Hero section
        st.markdown("""
        <div class="hero-section">
            <h1>🚀 Your One-Stop Robotics Components Store</h1>
            <p style='font-size: 1.3rem;'>Discover the best Arduino boards, sensors, motors, and robotics kits for your next innovative project!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Total Products", len(self.products), delta=f"+{len(self.products)}")
        with col2:
            st.metric("🏷️ Categories", len(self.categories), delta=f"+{len(self.categories)}")
        with col3:
            st.metric("🛒 Your Cart Items", len(st.session_state.cart))
        with col4:
            total_value = sum(item['price'] * item['quantity'] for item in st.session_state.cart)
            st.metric("💰 Cart Value", f"₹{total_value}")
        
        # Categories
        st.subheader("🛍️ Shop by Category")
        cols = st.columns(4)
        for idx, category in enumerate(self.categories):
            with cols[idx % 4]:
                # Use predefined gradient for category cards to avoid the method call issue
                category_colors = {
                    "Development Boards": ("#FF6B6B", "#E05555"),
                    "Sensors": ("#4ECDC4", "#45B8AF"), 
                    "Motors": ("#45B7D1", "#3DA5C0"),
                    "Wheels": ("#96CEB4", "#87BDA2"),
                    "Cameras": ("#FFEAA7", "#E6D296"),
                    "Batteries": ("#DDA0DD", "#C990CC"),
                    "Wires & Components": ("#98D8C8", "#89C5B7"),
                    "Project Kits": ("#F7DC6F", "#DEC75E")
                }
                
                base_color, dark_color = category_colors.get(category['name'], ("#667eea", "#764ba2"))
                
                if st.button(
                    f"{category['icon']} {category['name']}",
                    key=f"cat_{category['id']}",
                    use_container_width=True
                ):
                    st.session_state.current_category = category['name']
                    st.session_state.current_page = "Products"
                    st.rerun()
        
        # Featured products
        st.subheader("🔥 Featured Products")
        if not self.products.empty:
            self.display_products(self.products.head(8))
        else:
            st.info("No products available yet.")
    
    def display_products(self, products_df):
        """Display products in a responsive grid layout"""
        if products_df.empty:
            st.info("No products found matching your criteria.")
            return
        
        # Create responsive columns based on screen size
        cols_per_row = 4
        cols = st.columns(cols_per_row)
        
        for idx, (_, product) in enumerate(products_df.iterrows()):
            with cols[idx % cols_per_row]:
                self.display_product_card(product)
    
    def display_product_card(self, product):
        """Display individual product card with animations"""
        with st.container():
            st.markdown('<div class="product-card animated-card">', unsafe_allow_html=True)
            
            # Product image
            try:
                image = self.load_product_image(product['image'])
                st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading image: {e}")
            
            # Product details
            st.subheader(product['name'])
            st.write(f"**Category:** {product['category']}")
            
            # Price with gradient
            st.markdown(f'<div class="price-tag">₹{product["price"]}</div>', unsafe_allow_html=True)
            
            # Rating with stars
            stars = "⭐" * int(product['rating'])
            st.write(f"{stars} ({product['rating']})")
            
            # Stock status with colored badges
            stock_status = self.get_stock_status(product['stock'])
            st.markdown(f'<span class="stock-badge {stock_status["class"]}">{stock_status["text"]}</span>', unsafe_allow_html=True)
            
            # Action buttons in columns
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🛒 Add to Cart", key=f"add_{product['id']}", use_container_width=True):
                    self.add_to_cart(product)
                    st.success(f"✅ Added {product['name']} to cart!")
            with col2:
                if st.button("👀 View Details", key=f"view_{product['id']}", use_container_width=True):
                    st.session_state.view_product = product.to_dict()
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def get_stock_status(self, stock):
        """Get stock status with appropriate styling"""
        if stock > 10:
            return {"class": "in-stock", "text": f"In Stock ({stock})"}
        elif stock > 0:
            return {"class": "low-stock", "text": f"Low Stock ({stock})"}
        else:
            return {"class": "out-of-stock", "text": "Out of Stock"}
    
    def add_to_cart(self, product):
        """Add product to cart with animation effect"""
        cart_item = {
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'image': product['image'],
            'quantity': 1
        }
        
        # Check if item already in cart
        for item in st.session_state.cart:
            if item['id'] == product['id']:
                item['quantity'] += 1
                break
        else:
            st.session_state.cart.append(cart_item)
    
    def products_page(self):
        """Products listing page with filters"""
        st.title("📦 All Products")
        
        # Check if viewing single product
        if st.session_state.view_product is not None:
            self.product_detail_page()
            return
        
        # Filters in expandable section
        with st.expander("🔍 Filter Products", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_category = st.selectbox(
                    "Filter by Category",
                    ["All"] + [cat['name'] for cat in self.categories]
                )
            with col2:
                max_price = int(self.products['price'].max()) if not self.products.empty else 1000
                price_range = st.slider(
                    "💰 Price Range (₹)",
                    min_value=0,
                    max_value=max_price,
                    value=(0, max_price)
                )
            with col3:
                sort_by = st.selectbox(
                    "📊 Sort by",
                    ["Default", "Price: Low to High", "Price: High to Low", "Rating", "Name"]
                )
        
        # Filter products
        filtered_products = self.products.copy()
        
        if selected_category != "All":
            filtered_products = filtered_products[filtered_products['category'] == selected_category]
        
        filtered_products = filtered_products[
            (filtered_products['price'] >= price_range[0]) & 
            (filtered_products['price'] <= price_range[1])
        ]
        
        # Sort products
        if sort_by == "Price: Low to High":
            filtered_products = filtered_products.sort_values('price')
        elif sort_by == "Price: High to Low":
            filtered_products = filtered_products.sort_values('price', ascending=False)
        elif sort_by == "Rating":
            filtered_products = filtered_products.sort_values('rating', ascending=False)
        elif sort_by == "Name":
            filtered_products = filtered_products.sort_values('name')
        
        # Display products count
        st.write(f"**Showing {len(filtered_products)} products**")
        
        # Display products in responsive grid
        self.display_products(filtered_products)
    
    def product_detail_page(self):
        """Product detail page"""
        if st.session_state.view_product is None:
            st.error("No product selected!")
            st.session_state.current_page = "Products"
            st.rerun()
            return
        
        product = st.session_state.view_product
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="animated-card">', unsafe_allow_html=True)
            try:
                image = self.load_product_image(product['image'])
                st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading image: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="animated-card">', unsafe_allow_html=True)
            st.title(product['name'])
            st.markdown(f'<div class="price-tag">₹{product["price"]}</div>', unsafe_allow_html=True)
            
            # Rating
            stars = "⭐" * int(product['rating'])
            st.write(f"{stars} ({product['rating']})")
            
            st.write(f"**Category:** {product['category']}")
            
            # Stock status
            stock_status = self.get_stock_status(product['stock'])
            st.markdown(f'<span class="stock-badge {stock_status["class"]}">{stock_status["text"]}</span>', unsafe_allow_html=True)
            
            st.subheader("📝 Description")
            st.write(product['description'])
            
            if 'features' in product:
                st.subheader("✨ Features")
                for feature in product['features']:
                    st.write(f"✅ {feature}")
            
            # Add to cart section
            st.subheader("🛒 Add to Cart")
            col_qty, col_btn = st.columns([1, 2])
            with col_qty:
                quantity = st.number_input("Quantity", min_value=1, max_value=product['stock'], value=1, key="detail_qty")
            with col_btn:
                if st.button("🛒 Add to Cart", use_container_width=True, type="primary"):
                    for _ in range(quantity):
                        self.add_to_cart(product)
                    st.success(f"✅ Added {quantity} {product['name']} to cart!")
                    time.sleep(1)
                    st.rerun()
            
            if st.button("← Back to Products", use_container_width=True):
                st.session_state.view_product = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    def cart_page(self):
        """Shopping cart page"""
        st.title("🛒 Your Shopping Cart")
        
        if not st.session_state.cart:
            st.info("Your cart is empty! 🛍️")
            st.write("Browse our amazing products and add items to your cart!")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Start Shopping", use_container_width=True):
                    st.session_state.current_page = "Products"
                    st.rerun()
            return
        
        total_amount = 0
        
        for idx, item in enumerate(st.session_state.cart):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"**{item['name']}**")
                st.write(f"Price: ₹{item['price']}")
            
            with col2:
                quantity = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=10,
                    value=item['quantity'],
                    key=f"qty_{idx}"
                )
                if quantity != item['quantity']:
                    item['quantity'] = quantity
            
            with col3:
                item_total = item['price'] * item['quantity']
                st.write(f"**Total:** ₹{item_total}")
                total_amount += item_total
            
            with col4:
                if st.button("🗑️ Remove", key=f"del_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
            
            st.divider()
        
        st.markdown(f"<h2>💰 Total: ₹{total_amount}</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Update Cart", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("🛍️ Continue Shopping", use_container_width=True):
                st.session_state.current_page = "Products"
                st.rerun()
        with col3:
            if st.button("🚀 Checkout", use_container_width=True, type="primary"):
                st.session_state.checkout_total = total_amount
                st.session_state.current_page = "Checkout"
                st.rerun()
    
    def checkout_page(self):
        """Checkout page"""
        st.title("🚀 Checkout")
        
        # Check if we should show order success message
        if st.session_state.get('show_order_success', False):
            st.success(f"🎉 Order placed successfully!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 View Orders", use_container_width=True):
                    st.session_state.show_order_success = False
                    st.session_state.current_page = "Orders"
                    st.rerun()
            with col2:
                if st.button("🛍️ Continue Shopping", use_container_width=True):
                    st.session_state.show_order_success = False
                    st.session_state.current_page = "Products"
                    st.rerun()
            return
        
        if not st.session_state.cart:
            st.error("Your cart is empty!")
            st.session_state.current_page = "Cart"
            st.rerun()
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="animated-card">', unsafe_allow_html=True)
            st.subheader("📦 Shipping Details")
            with st.form("checkout_form"):
                name = st.text_input("👤 Full Name", value=st.session_state.user['name'] if st.session_state.user else "")
                email = st.text_input("📧 Email", value=st.session_state.user['email'] if st.session_state.user else "")
                phone = st.text_input("📱 Phone Number", value="9876543210")
                address = st.text_area("🏠 Shipping Address", value="123 Main Street")
                city = st.text_input("🏙️ City", value="Mumbai")
                state = st.text_input("🗺️ State", value="Maharashtra")
                pincode = st.text_input("📮 Pincode", value="400001")
                
                st.subheader("💳 Payment Method")
                payment_method = st.radio(
                    "Select Payment Method",
                    ["Credit/Debit Card", "UPI", "Cash on Delivery", "Net Banking"]
                )
                
                if st.form_submit_button("✅ Place Order", type="primary", use_container_width=True):
                    if all([name, email, phone, address, city, state, pincode]):
                        self.place_order(name, email, phone, address, city, state, pincode, payment_method)
                        st.rerun()
                    else:
                        st.error("❌ Please fill all the fields!")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="animated-card">', unsafe_allow_html=True)
            st.subheader("📋 Order Summary")
            for item in st.session_state.cart:
                st.write(f"• {item['name']} x {item['quantity']} - ₹{item['price'] * item['quantity']}")
            
            st.markdown(f"**💰 Total Amount: ₹{st.session_state.checkout_total}**")
            
            # Payment options visualization
            if 'payment_method' in locals():
                if payment_method == "Cash on Delivery":
                    st.info("💰 Pay when you receive your order")
                elif payment_method == "UPI":
                    st.info("📱 Pay using UPI ID or QR Code")
                else:
                    st.info("💳 Secure payment gateway")
            st.markdown('</div>', unsafe_allow_html=True)
    
    def place_order(self, name, email, phone, address, city, state, pincode, payment_method):
        """Place order and clear cart"""
        order = {
            'order_id': f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'customer': {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'city': city,
                'state': state,
                'pincode': pincode
            },
            'items': st.session_state.cart.copy(),
            'total_amount': st.session_state.checkout_total,
            'payment_method': payment_method,
            'status': 'Confirmed',
            'order_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        st.session_state.orders.append(order)
        st.session_state.cart = []
        if 'checkout_total' in st.session_state:
            del st.session_state.checkout_total
        
        # Set flag to show success message instead of using button inside form
        st.session_state.show_order_success = True
    
    def orders_page(self):
        """Order history page"""
        st.title("📋 Your Orders")
        
        if not st.session_state.orders:
            st.info("You haven't placed any orders yet! 🛍️")
            if st.button("🚀 Start Shopping", use_container_width=True):
                st.session_state.current_page = "Products"
                st.rerun()
            return
        
        for order in reversed(st.session_state.orders):
            with st.expander(f"📦 Order {order['order_id']} - ₹{order['total_amount']} - {order['status']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 Order Details")
                    st.write(f"**📅 Order Date:** {order['order_date']}")
                    st.write(f"**📊 Status:** {order['status']}")
                    st.write(f"**💳 Payment Method:** {order['payment_method']}")
                    st.write(f"**💰 Total Amount:** ₹{order['total_amount']}")
                
                with col2:
                    st.subheader("🏠 Shipping Address")
                    st.write(f"**👤 Name:** {order['customer']['name']}")
                    st.write(f"**🏠 Address:** {order['customer']['address']}")
                    st.write(f"**🏙️ City:** {order['customer']['city']}")
                    st.write(f"**🗺️ State:** {order['customer']['state']}")
                    st.write(f"**📮 Pincode:** {order['customer']['pincode']}")
                
                st.subheader("🛍️ Order Items")
                for item in order['items']:
                    st.write(f"• {item['name']} x {item['quantity']} - ₹{item['price'] * item['quantity']}")
    
    def admin_dashboard(self):
        """Admin dashboard for analytics"""
        st.title("📊 Analytics Dashboard")
        
        if not st.session_state.user:
            st.error("Please login to access analytics dashboard")
            return
        
        # Sales analytics
        total_orders = len(st.session_state.orders)
        total_revenue = sum(order['total_amount'] for order in st.session_state.orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Total Orders", total_orders, delta=f"+{total_orders}")
        col2.metric("💰 Total Revenue", f"₹{total_revenue:,.2f}", delta=f"₹{total_revenue:,.0f}")
        col3.metric("📊 Average Order", f"₹{avg_order_value:,.2f}")
        col4.metric("👥 Active Users", "1", delta="+1")
        
        if not self.products.empty:
            # Product analytics
            st.subheader("📈 Product Analytics")
            
            # Category-wise average price
            category_sales = self.products.groupby('category')['price'].mean().reset_index()
            fig = px.bar(
                category_sales, 
                x='category', 
                y='price', 
                title="Average Price by Category",
                color='price',
                color_continuous_scale='viridis'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Inventory management
            st.subheader("📦 Inventory Management")
            low_stock = self.products[self.products['stock'] < 10]
            if not low_stock.empty:
                st.warning("⚠️ Low Stock Alert!")
                st.dataframe(low_stock[['name', 'category', 'stock']], use_container_width=True)
            else:
                st.success("✅ All products have sufficient stock!")
    
    def main(self):
        """Main application controller"""
        
        # Check if user is logged in
        if st.session_state.user is None:
            self.login_page()
            return
        
        # Show sidebar navigation
        self.sidebar_navigation()
        
        # Route to appropriate page
        current_page = st.session_state.current_page
        
        if current_page == "Home":
            self.home_page()
        elif current_page == "Products":
            self.products_page()
        elif current_page == "Cart":
            self.cart_page()
        elif current_page == "Checkout":
            self.checkout_page()
        elif current_page == "Orders":
            self.orders_page()
        elif current_page == "Analytics":
            self.admin_dashboard()

# Run the application
if __name__ == "__main__":
    app = RoboticsStore()
    app.main()
