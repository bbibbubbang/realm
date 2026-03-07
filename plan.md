We will use CheerpJ to run the Minecraft jar in the browser.

1. Gather all compiled classes from `src/main/java/` into a single jar file named `minecraft.jar`.
2. Create an `index.html` file that includes the CheerpJ loader and initializes it to run the main class `net.minecraft.client.Minecraft` from `minecraft.jar`. We will use CheerpJ version 3 since it has improved WebGL and LWJGL support.
3. Verify that the jar contains the necessary LWJGL libraries or add them. Wait, Minecraft usually requires native LWJGL libraries. With CheerpJ, it intercepts some LWJGL calls, but it might still need the LWJGL java classes. Let's check if the jar has them.
