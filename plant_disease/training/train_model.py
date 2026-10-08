import os
import random
import torch

from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from torch import nn, optim


# ============================================================
# PROJECT 26 - PLANT DISEASE DETECTION
# MobileNetV2 Transfer Learning
# ============================================================

# -----------------------------
# Paths
# -----------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset",
    "images",
    "raw",
    "color"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# -----------------------------
# Configuration
# -----------------------------

IMAGE_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 5
VALIDATION_SPLIT = 0.20

LEARNING_RATE = 0.0001

SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)


# -----------------------------
# Device
# -----------------------------

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 70)
print("PROJECT 26 - PLANT DISEASE DETECTION")
print("MobileNetV2 Transfer Learning")
print("=" * 70)

print(f"Device: {device}")
print(f"Dataset: {DATASET_DIR}")


# ============================================================
# DATA TRANSFORMS
# ============================================================

train_transform = transforms.Compose([

    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

    transforms.RandomHorizontalFlip(),

    transforms.RandomRotation(10),

    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


validation_transform = transforms.Compose([

    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading dataset...")

full_dataset = datasets.ImageFolder(
    root=DATASET_DIR,
    transform=train_transform
)

num_classes = len(full_dataset.classes)
total_images = len(full_dataset)

print(f"Total images : {total_images}")
print(f"Total classes: {num_classes}")


# ============================================================
# TRAIN / VALIDATION SPLIT
# ============================================================

validation_size = int(
    total_images * VALIDATION_SPLIT
)

training_size = total_images - validation_size

train_dataset, validation_dataset = random_split(
    full_dataset,
    [training_size, validation_size],
    generator=torch.Generator().manual_seed(SEED)
)

print("\nDataset split:")
print(f"Training images   : {len(train_dataset)}")
print(f"Validation images : {len(validation_dataset)}")


# ============================================================
# DATA LOADERS
# ============================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

validation_loader = DataLoader(
    validation_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


# ============================================================
# LOAD MOBILENETV2
# ============================================================

print("\nLoading MobileNetV2...")

weights = models.MobileNet_V2_Weights.DEFAULT

model = models.mobilenet_v2(
    weights=weights
)


# Freeze pretrained layers

for parameter in model.features.parameters():
    parameter.requires_grad = False


# Replace final classifier

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    num_classes
)

model = model.to(device)


# ============================================================
# LOSS + OPTIMIZER
# ============================================================

criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.classifier[1].parameters(),
    lr=LEARNING_RATE
)


# ============================================================
# TRAINING
# ============================================================

best_validation_accuracy = 0.0

best_model_path = os.path.join(
    MODEL_DIR,
    "plant_disease_mobilenetv2.pth"
)


for epoch in range(EPOCHS):

    print("\n")
    print("=" * 70)
    print(f"Epoch {epoch + 1}/{EPOCHS}")
    print("=" * 70)

    # -------------------------
    # Training
    # -------------------------

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for batch_index, (images, labels) in enumerate(train_loader):

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

        _, predicted = torch.max(
            outputs,
            1
        )

        total += labels.size(0)

        correct += (
            predicted == labels
        ).sum().item()

        if (batch_index + 1) % 100 == 0:

            print(
                f"Batch {batch_index + 1} | "
                f"Loss: {loss.item():.4f}"
            )

    training_accuracy = (
        100 * correct / total
    )

    training_loss = (
        running_loss / len(train_loader)
    )


    # -------------------------
    # Validation
    # -------------------------

    model.eval()

    validation_loss = 0.0
    validation_correct = 0
    validation_total = 0

    with torch.no_grad():

        for images, labels in validation_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            validation_loss += loss.item()

            _, predicted = torch.max(
                outputs,
                1
            )

            validation_total += labels.size(0)

            validation_correct += (
                predicted == labels
            ).sum().item()


    validation_accuracy = (
        100 * validation_correct / validation_total
    )

    validation_loss = (
        validation_loss / len(validation_loader)
    )


    # -------------------------
    # Results
    # -------------------------

    print("\nEpoch Results:")

    print(
        f"Training Loss      : {training_loss:.4f}"
    )

    print(
        f"Training Accuracy  : {training_accuracy:.2f}%"
    )

    print(
        f"Validation Loss    : {validation_loss:.4f}"
    )

    print(
        f"Validation Accuracy: {validation_accuracy:.2f}%"
    )


    # -------------------------
    # Save best model
    # -------------------------

    if validation_accuracy > best_validation_accuracy:

        best_validation_accuracy = validation_accuracy

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "classes": full_dataset.classes,
                "num_classes": num_classes,
                "image_size": IMAGE_SIZE,
                "validation_accuracy": validation_accuracy
            },
            best_model_path
        )

        print("\n✅ Best model saved!")

        print(
            f"Path: {best_model_path}"
        )


# ============================================================
# COMPLETED
# ============================================================

print("\n")
print("=" * 70)
print("TRAINING COMPLETED")
print("=" * 70)

print(
    f"Best validation accuracy: "
    f"{best_validation_accuracy:.2f}%"
)

print(
    f"Model saved at:\n{best_model_path}"
)

print("=" * 70)