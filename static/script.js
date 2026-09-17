// ----------------------------------------------------
// Get HTML elements
// ----------------------------------------------------

const predictionForm =
    document.getElementById("predictionForm");

const resultCard =
    document.getElementById("resultCard");

const predictionElement =
    document.getElementById("prediction");

const loading =
    document.getElementById("loading");

const yesButton =
    document.getElementById("yesButton");

const noButton =
    document.getElementById("noButton");

const correctionBox =
    document.getElementById("correctionBox");

const submitCorrection =
    document.getElementById("submitCorrection");

const actualPriceInput =
    document.getElementById("actualPrice");

const feedbackMessage =
    document.getElementById("feedbackMessage");


// ----------------------------------------------------
// Store current property data
// ----------------------------------------------------

let currentProperty = null;


// ----------------------------------------------------
// Format Indian currency
// ----------------------------------------------------

function formatIndianCurrency(value) {

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(value);

}


// ----------------------------------------------------
// Animate price
// ----------------------------------------------------

function animatePrice(targetValue) {

    let current = 0;

    const duration = 1000;

    const steps = 40;

    const increment = targetValue / steps;

    let step = 0;

    const interval = setInterval(() => {

        current += increment;

        step++;

        if (step >= steps) {

            current = targetValue;

            clearInterval(interval);

        }

        predictionElement.textContent =
            formatIndianCurrency(current);

    }, duration / steps);

}


// ----------------------------------------------------
// Prediction form
// ----------------------------------------------------

predictionForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        // ------------------------------------------------
        // Read values from form
        // ------------------------------------------------

        const location =
            document.getElementById("location").value;

        const area =
            document.getElementById("area").value;

        const bedrooms =
            document.getElementById("bedrooms").value;

        const age =
            document.getElementById("age").value;

        const bathrooms =
            document.getElementById("bathrooms").value;

        const parking =
            document.querySelector(
                'input[name="parking"]:checked'
            ).value;

        const propertyType =
            document.getElementById("propertyType").value;


        // ------------------------------------------------
        // Store current property
        // ------------------------------------------------

        currentProperty = {

            location: location,

            area: area,

            bedrooms: bedrooms,

            age: age,

            bathrooms: bathrooms,

            parking: parking,

            property_type: propertyType

        };


        // ------------------------------------------------
        // Show loading
        // ------------------------------------------------

        loading.classList.remove("hidden");

        resultCard.classList.add("hidden");

        feedbackMessage.textContent = "";

        correctionBox.classList.add("hidden");


        try {

            // --------------------------------------------
            // Send request to Flask
            // --------------------------------------------

            const response = await fetch(
                "/predict",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        currentProperty
                    )

                }
            );


            const data =
                await response.json();


            if (!data.success) {

                throw new Error(data.error);

            }


            // --------------------------------------------
            // Display result
            // --------------------------------------------

            resultCard.classList.remove("hidden");

            animatePrice(data.prediction);


        }

        catch (error) {

            alert(
                "Prediction failed: " +
                error.message
            );

        }

        finally {

            loading.classList.add("hidden");

        }

    }
);


// ----------------------------------------------------
// YES button
// ----------------------------------------------------

yesButton.addEventListener(
    "click",
    function() {

        correctionBox.classList.add("hidden");

        feedbackMessage.textContent =
            "Thank you for your feedback!";

    }
);


// ----------------------------------------------------
// NO button
// ----------------------------------------------------

noButton.addEventListener(
    "click",
    function() {

        correctionBox.classList.remove("hidden");

        actualPriceInput.focus();

        feedbackMessage.textContent = "";

    }
);


// ----------------------------------------------------
// Submit correction
// ----------------------------------------------------

submitCorrection.addEventListener(
    "click",
    async function() {

        const actualPrice =
            actualPriceInput.value;


        if (!actualPrice || actualPrice <= 0) {

            alert(
                "Please enter a valid actual price."
            );

            return;

        }


        // Combine property details + actual price

        const correctionData = {

            ...currentProperty,

            actual_price: actualPrice

        };


        submitCorrection.disabled = true;

        submitCorrection.textContent =
            "Retraining model...";


        try {

            // --------------------------------------------
            // Send correction to Flask
            // --------------------------------------------

            const response = await fetch(
                "/feedback",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        correctionData
                    )

                }
            );


            const data =
                await response.json();


            if (!data.success) {

                throw new Error(data.error);

            }


            feedbackMessage.textContent =
                "✓ " + data.message;

            actualPriceInput.value = "";

            correctionBox.classList.add("hidden");


        }

        catch (error) {

            feedbackMessage.textContent =
                "Error: " + error.message;

        }

        finally {

            submitCorrection.disabled = false;

            submitCorrection.textContent =
                "Submit Correction";

        }

    }
);