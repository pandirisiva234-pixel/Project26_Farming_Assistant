import os
import sys
import torch

from PIL import Image
from torchvision import transforms, models
from torch import nn


# ============================================================
# PROJECT 26 - PLANT DISEASE PREDICTION
# MobileNetV2
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "plant_disease_mobilenetv2.pth"
)


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# LOAD MODEL CHECKPOINT
# ============================================================

print("Loading trained model...")

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)

classes = checkpoint["classes"]
num_classes = checkpoint["num_classes"]
image_size = checkpoint["image_size"]


# ============================================================
# CREATE MOBILENETV2
# ============================================================

model = models.mobilenet_v2(
    weights=None
)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    num_classes
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)

model.eval()


print("Model loaded successfully!")
print(f"Classes: {num_classes}")
print(f"Device: {device}")


# ============================================================
# IMAGE TRANSFORMATION
# ============================================================

transform = transforms.Compose([

    transforms.Resize(
        (image_size, image_size)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_image(image_path):

    if not os.path.exists(image_path):

        print(
            f"\nImage not found:\n{image_path}"
        )

        return


    image = Image.open(
        image_path
    ).convert("RGB")


    image_tensor = transform(
        image
    ).unsqueeze(0).to(device)


    with torch.no_grad():

        outputs = model(
            image_tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, predicted = torch.max(
            probabilities,
            1
        )


    predicted_class = classes[
        predicted.item()
    ]

    confidence_percentage = (
        confidence.item() * 100
    )


    print("\n")
    print("=" * 60)
    print("PLANT DISEASE PREDICTION")
    print("=" * 60)

    print(
        f"Image     : {image_path}"
    )

    print(
        f"Prediction: {predicted_class}"
    )

    print(
        f"Confidence: {confidence_percentage:.2f}%"
    )

    print("=" * 60)


# ============================================================
# COMMAND LINE INPUT
# ============================================================

if len(sys.argv) < 2:

    print("\nUsage:")

    print(
        "python .\\training\\predict.py "
        "\"path_to_leaf_image\""
    )

    print("\nExample:")

    print(
        'python .\\training\\predict.py '
        '"C:\\Users\\p.sivaram\\Desktop\\leaf.jpg"'
    )

    sys.exit()


image_path = sys.argv[1]

predict_image(
    image_path
)