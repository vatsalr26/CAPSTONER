document.addEventListener("DOMContentLoaded", () => {
  document
    .getElementById("fileUploadForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();

      let fileInput = document.getElementById("file").files[0];
      if (!fileInput) {
        alert("Please select a file to upload.");
        return;
      }

      let formData = new FormData();
      formData.append("file", fileInput);

      try {
        let response = await fetch("/analyze", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        let result = await response.json();
        document.getElementById("output").innerHTML = `
                <pre>${JSON.stringify(result, null, 2)}</pre>
            `;
      } catch (error) {
        console.error("Error:", error);
        document.getElementById("output").innerHTML =
          `<p style="color: red;">Error: ${error.message}</p>`;
      }
    });
});
