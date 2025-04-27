# Telegram Logo Bot

<div style="text-align: center; padding: 20px; background-color: #f0f4f8; border-radius: 10px;">
  <h1 style="color: #2c3e50;">Telegram Logo Bot</h1>
  <p style="font-size: 18px; color: #34495e;">
    A Telegram bot that creates custom logo images by adding text to HD backgrounds with various styles. Supports multiple languages, including Khmer, with customizable fonts.
  </p>
  <img src="https://via.placeholder.com/400x200.png?text=Logo+Bot+Preview" alt="Bot Preview" style="border-radius: 8px; margin: 10px;" />
</div>

## Features

<div style="margin: 20px 0;">
  <ul style="list-style-type: none; padding: 0;">
    <li style="margin: 10px 0;"><strong>🌐 Multilingual Support:</strong> 11 languages (English, Khmer, Thai, Vietnamese, Portuguese, Chinese, Japanese, Hindi, Arabic, Korean, Spanish).</li>
    <li style="margin: 10px 0;"><strong>✍️ Custom Fonts:</strong> Upload <code>.ttf</code> fonts or use defaults (e.g., NotoSansKhmer for Khmer).</li>
    <li style="margin: 10px 0;"><strong>🎨 Text Styles:</strong> 60 styles (Elegant Gold, 3D Cyan, etc.) from <code>text_styles.json</code>.</li>
    <li style="margin: 10px 0;"><strong>🖼️ HD Backgrounds:</strong> Random images from <code>image_urls.json</code>.</li>
    <li style="margin: 10px 0;"><strong>🖱️ User-Friendly:</strong> Inline keyboard for easy navigation.</li>
    <li style="margin: 10px 0;"><strong>💾 Data Persistence:</strong> User preferences saved in <code>bot_data.json</code>.</li>
    <li style="margin: 10px 0;"><strong>📢 Admin Features:</strong> Broadcast messages with <code>/broadcast</code>.</li>
  </ul>
</div>

## Commands

<div style="background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0;">
  <h2 style="color: #2980b9;">Available Commands</h2>
  <ul style="list-style-type: disc; margin-left: 20px;">
    <li><code>/start</code>: Welcome message with inline keyboard.</li>
    <li><code>/setfont</code>: Upload a <code>.ttf</code> font.</li>
    <li><code>/styles</code>: List all text styles.</li>
    <li><code>/fonts</code>: List default fonts for each language.</li>
    <li><code>/style [number or name]</code>: Set style (e.g., <code>/style 1</code> or <code>/style Elegant Gold</code>).</li>
    <li><code>/randomstyle</code>: Use random styles.</li>
    <li><code>/language [code]</code>: Set language (e.g., <code>/language kh</code>).</li>
    <li><code>/tutorial</code>: Usage instructions.</li>
    <li><code>/broadcast [message]</code>: Send message to all users (admin only).</li>
  </ul>
</div>

## Setup

<div style="margin: 20px 0;">
  <h2 style="color: #27ae60;">Getting Started</h2>

  <h3>Prerequisites</h3>
  <ul style="list-style-type: circle; margin-left: 20px;">
    <li>Python 3.8+</li>
    <li>Pydroid 3 (for Android) or any Python environment</li>
    <li>Telegram bot token from <a href="https://t.me/BotFather" style="color: #2980b9;">BotFather</a></li>
  </ul>

  <h3>Installation</h3>
  <ol style="margin-left: 20px;">
    <li><strong>Clone the Repository:</strong>
      <pre style="background-color: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px;">
git clone https://github.com/yourusername/telegram-logo-bot.git
cd telegram-logo-bot
      </pre>
    </li>
    <li><strong>Install Dependencies:</strong>
      <pre style="background-color: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px;">
pip install -r install.txt
      </pre>
      Or:
      <pre style="background-color: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px;">
pip install python-telegram-bot==20.7 Pillow requests
      </pre>
    </li>
    <li><strong>Directory Structure:</strong>
      <pre style="background-color: #ecf0f1; padding: 10px; border-radius: 5px;">
telegram-logo-bot/
├── main.py
├── install.txt
├── image_urls.json
├── text_styles.json
├── languages.json
├── bot_data.json (created automatically)
├── font/
│   ├── en/Roboto-Regular.ttf
│   ├── kh/NotoSansKhmer-Regular.ttf
│   ├── th/THSarabunPSK-Regular.ttf
│   ├── vi/Quicksand-Regular.ttf
│   ├── pt/Lato-Regular.ttf
│   ├── zh/NotoSansSC-Regular.ttf
│   ├── ja/NotoSansJP-Regular.ttf
│   ├── hi/NotoSansDevanagari-Regular.ttf
│   ├── ar/NotoNaskhArabic-Regular.ttf
│   ├── ko/NotoSansKR-Regular.ttf
│   ├── es/OpenSans-Regular.ttf
└── user_fonts/ (created automatically)
      </pre>
    </li>
    <li><strong>Download Fonts:</strong>
      <p>Download from <a href="https://fonts.google.com/" style="color: #2980b9;">Google Fonts</a> or other sources:</p>
      <ul style="list-style-type: square; margin-left: 20px;">
        <li>Roboto-Regular.ttf (English)</li>
        <li>NotoSansKhmer-Regular.ttf (Khmer)</li>
        <li>THSarabunPSK-Regular.ttf (Thai, from f0nt.com)</li>
        <li>Quicksand-Regular.ttf (Vietnamese)</li>
        <li>Lato-Regular.ttf (Portuguese)</li>
        <li>NotoSansSC-Regular.ttf (Chinese)</li>
        <li>NotoSansJP-Regular.ttf (Japanese)</li>
        <li>NotoSansDevanagari-Regular.ttf (Hindi)</li>
        <li>NotoNaskhArabic-Regular.ttf (Arabic)</li>
        <li>NotoSansKR-Regular.ttf (Korean)</li>
        <li>OpenSans-Regular.ttf (Spanish)</li>
      </ul>
      <p>Place fonts in their respective <code>font/&lt;lang&gt;/</code> folders.</p>
    </li>
    <li><strong>Configure Bot Token:</strong>
      <p>In <code>main.py</code>, replace:</p>
      <pre style="background-color: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px;">
TOKEN = "8049198861:YourTokensjawi1888Uahaban"
      </pre>
      <p>With your bot token. Update <code>ADMIN_ID</code> with your Telegram user ID (find via <a href="https://t.me/userinfobot" style="color: #2980b9;">@userinfobot</a>).</p>
    </li>
    <li><strong>Run the Bot:</strong>
      <pre style="background-color: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px;">
python main.py
      </pre>
    </li>
  </ol>
</div>

## Usage

<div style="margin: 20px 0;">
  <h2 style="color: #d35400;">How to Use</h2>
  <ol style="margin-left: 20px;">
    <li><strong>Start:</strong> Send <code>/start</code> to see the welcome message and inline keyboard.</li>
    <li><strong>Set Language:</strong> Send <code>/language kh</code> for Khmer or <code>/language en</code> for English.</li>
    <li><strong>List Fonts:</strong> Send <code>/fonts</code> to see default fonts.</li>
    <li><strong>Upload Font:</strong> Send <code>/setfont</code> and attach a <code>.ttf</code> file.</li>
    <li><strong>Add Text:</strong> Send text (e.g., “សួស្តី” for Khmer “Hello”) to generate an image.</li>
    <li><strong>Choose Style:</strong> Send <code>/styles</code>, then <code>/style 1</code> or <code>/style Elegant Gold</code>.</li>
    <li><strong>Random Style:</strong> Send <code>/randomstyle</code>.</li>
    <li><strong>Broadcast:</strong> Admin sends <code>/broadcast Hello!</code> to message all users.</li>
  </ol>

  <h3>Example</h3>
  <div style="background-color: #f9e79f; padding: 15px; border-radius: 8px;">
    <p>1. Send <code>/language kh</code>.</p>
    <p>2. Send <code>/setfont</code> with <code>NotoSansKhmer-Regular.ttf</code>.</p>
    <p>3. Send <code>/style Elegant Gold</code>.</p>
    <p>4. Send “សួស្តី”.</p>
    <p>5. Receive an image with “សួស្តី” in Elegant Gold style.</p>
  </div>
</div>

## Notes

<div style="background-color: #fce4ec; padding: 15px; border-radius: 8px; margin: 20px 0;">
  <h2 style="color: #c0392b;">Important Notes</h2>
  <ul style="list-style-type: disc; margin-left: 20px;">
    <li><strong>Font Issues:</strong> Missing fonts (e.g., <code>NotoSansKhmer-Regular.ttf</code>) may cause rendering issues for non-Latin scripts. Ensure fonts are in <code>font/&lt;lang&gt;/</code>.</li>
    <li><strong>Language Rendering:</strong> Hindi or Arabic may not render correctly without proper fonts. Use compatible fonts (e.g., <code>NotoSansDevanagari-Regular.ttf</code>).</li>
    <li><strong>Translations:</strong> Incomplete <code>languages.json</code> entries fall back to English. Update the file as needed.</li>
    <li><strong>Image URLs:</strong> Some URLs in <code>image_urls.json</code> may fail. Update with valid URLs.</li>
    <li><strong>Pydroid 3:</strong> Grant storage permissions for file access on Android.</li>
  </ul>
</div>

## Contributing

<div style="margin: 20px 0;">
  <h2 style="color: #8e44ad;">Contribute</h2>
  <p>We welcome contributions! To contribute:</p>
  <ol style="margin-left: 20px;">
    <li>Fork the repository.</li>
    <li>Create a branch: <code>git checkout -b feature/your-feature</code>.</li>
    <li>Commit changes: <code>git commit -m "Add your feature"</code>.</li>
    <li>Push: <code>git push origin feature/your-feature</code>.</li>
    <li>Open a Pull Request.</li>
  </ol>
  <p>Report issues or suggest features via <a href="https://github.com/SeyhaLite/Telegram-Logo-Maker-Bot-Python-Free/issues" style="color: #2980b9;">GitHub Issues</a>.</p>
</div>

## License

<div style="margin: 20px 0;">
  <h2 style="color: #16a085;">License</h2>
  <p>This project is licensed under the MIT License. See the <a href="LICENSE" style="color: #2980b9;">LICENSE</a> file for details.</p>
</div>

## Contact

<div style="text-align: center; padding: 20px; background-color: #f0f4f8; border-radius: 10px; margin: 20px 0;">
  <h2 style="color: #2c3e50;">Get in Touch</h2>
  <p><strong>Demo Bot:</strong> <a href="https://t.me/SYLOGODesignBot" style="color: #2980b9;">@SYLOGODesignBot </a>( my bot can down or die cuz free host no 24/7 )</p>
  <p><strong>GitHub:</strong> <a href="[https://github.com/SeyhaLite](https://github.com/SeyhaLite/" style="color: #2980b9;">SeyhaLite</a></p>
  <p><strong>Email:</strong> SeyhaLite@gmail.com</p>
  <a href="https://t.me/SYLOGODesignBot" style="display: inline-block; background-color: #2980b9; color: #fff; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Try the Bot!</a>
</div>

## Donate Me

# BTC
bc1qrr2xlea0vtm8r6vmmkwz5tqajc4270pdqgmakn
 
# ETH
0xb7072412e6b66c4d46704075eb3c7658552e50f3

# USDT Tether (ERC20)
0xb7072412e6B66C4d46704075Eb3C7658552e50f3
