from flask import Flask, request

app = Flask(__name__)

@app.route('/digikey_callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    if code:
        print(f"Authorization Code: {code}")
        return "Authorization Code received! You can close this window.", 200
    else:
        return "Authorization failed or no code received.", 400

if __name__ == "__main__":
    app.run(host="localhost", port=8139, debug=True)