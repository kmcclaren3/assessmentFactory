import numpy as np
import matplotlib.pyplot as plt

# Parameters
years = np.arange(0, 13)  # K–12 (13 grade levels)
base_learning_rate = 1.0  # 1 year of learning per school year (typical)
sigma_boost = 2.0  # 2σ effect from Bloom (approx. +2 std deviations in performance)

# Model assumptions
# We'll assume Bloom's 2σ effect corresponds to roughly a 1.75x learning rate increase.
learning_rate_2sigma = 1.75  # midpoint estimate between 1.5x–2x

# Cumulative learning over time
traditional_learning = base_learning_rate * years
tutored_learning = learning_rate_2sigma * years

# Plot
plt.figure(figsize=(10, 6))
plt.plot(years, traditional_learning, label="Traditional Classroom", linewidth=2, color="steelblue")
plt.plot(years, tutored_learning, label="Bloom’s 2σ (Tutored/Mastery Learning)", 
         linewidth=2, color="darkorange", linestyle="--")

# Reference lines
plt.axhline(12, color="gray", linestyle=":", linewidth=1)
plt.axhline(14, color="gray", linestyle=":", linewidth=1)
plt.axhline(16, color="gray", linestyle=":", linewidth=1)
plt.text(12.1, 12, "High School Graduate", va="bottom", color="gray")
plt.text(12.1, 14, "College Sophomore", va="bottom", color="gray")
plt.text(12.1, 16, "College Graduate", va="bottom", color="gray")

plt.title("Theoretical Learning Progression: Bloom’s 2σ Effect in K–12 Education", fontsize=14)
plt.xlabel("Years of Schooling (K–12)")
plt.ylabel("Equivalent Grade Level of Learning Achieved")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
