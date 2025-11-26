# G4Med Test Template

This is the **Template Repository** for creating new Geant4 validation tests within the `G4Med-test`.

It comes pre-configured with:
* **Automatic CI/CD:** GitHub Actions to build and test your code.
* **Apptainer Integration:** Automatically builds a `.sif` container and pushes it to the GitHub Container Registry (GHCR).
* **Dynamic CMake:** Automatically adapts the project and executable name based on the repository name.

---

## 🚀 Quick Start: How to Create a New Test

### 1. Create the Repository
1.  Click the **[Use this template](https://github.com/G4Med-test/template-test/generate)** button at the top of this page.
2.  Select **Create a new repository**.
3.  **Owner:** Select `G4Med-test`.
4.  **Repository Name:** Choose a name (e.g., `HadronTest`, `ElectronScattering`).
    * *Note:* The name you choose here will automatically become the name of your executable and your container (e.g., `HadronTest.sif`).
5.  Click **Create repository**.