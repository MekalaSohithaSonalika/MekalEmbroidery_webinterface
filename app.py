from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

def read_dst(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    # DST header is 512 bytes
    header = data[:512]
    stitches = data[512:]
    return header, stitches

def merge_dst_files(files, output_file):
    # Read all files
    headers = []
    stitches = []
    
    for file in files:
        header, stitch = read_dst(file)
        headers.append(header)
        stitches.append(stitch)
    
    # Remove END bytes from all files except the last one
    for i in range(len(stitches)-1):
        if stitches[i][-3:] == b'\x00\x00\xf3':
            stitches[i] = stitches[i][:-3]
    
    # Combine all stitches and add END at the end
    merged_stitches = b''.join(stitches) + b'\x00\x00\xf3'
    
    # Write the merged file
    with open(output_file, 'wb') as f:
        f.write(headers[0])  # Use header from first file
        f.write(merged_stitches)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        word = request.form['word'].upper()
        word_length = len(word)
        
        if word_length < 1 or word_length > 10:
            return "Please enter a word between 1 and 10 letters", 400
        
        # Create list of DST files based on the word
        folder_name = f"letters{word_length}"
        dst_files = [os.path.join(folder_name, f"{letter}{word_length}.dst") for letter in word]
        
        # Check if all files exist
        for file in dst_files:
            if not os.path.exists(file):
                return f"File {file} not found", 404
        
        # Create output filename
        output_file = f"{word.lower()}.dst"
        
        # Merge the files
        merge_dst_files(dst_files, output_file)
        
        # Send the file to the user
        return send_file(output_file, as_attachment=True)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)