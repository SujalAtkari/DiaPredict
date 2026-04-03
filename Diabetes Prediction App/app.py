from flask import Flask, render_template, request
import numpy as np
import pickle
import os


app = Flask(__name__)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "hybrid_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")


with open(MODEL_PATH, "rb") as f:
	model = pickle.load(f)

with open(SCALER_PATH, "rb") as f:
	scaler = pickle.load(f)


FEATURE_NAMES = [
	"Pregnancies",
	"Glucose",
	"BloodPressure",
	"SkinThickness",
	"Insulin",
	"BMI",
	"DiabetesPedigreeFunction",
	"Age",
]


@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
	try:
		values = []
		for name in FEATURE_NAMES:
			raw = request.form.get(name)
			if raw is None or raw.strip() == "":
				return render_template(
					"result.html",
					prediction_text="Please fill in all fields.",
				)
			values.append(float(raw))

		input_array = np.array([values])
		scaled_input = scaler.transform(input_array)
		prediction = model.predict(scaled_input)[0]

		if int(prediction) == 1:
			message = "The model predicts: Diabetes Positive"
		else:
			message = "The model predicts: Diabetes Negative"

		return render_template("result.html", prediction_text=message)
	except Exception as e:
		return render_template(
			"result.html",
			prediction_text=f"Error while making prediction: {e}",
		)


if __name__ == "__main__":
	app.run(debug=True)
