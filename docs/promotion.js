// ===============================
// RSK32 PROMOTION PAGE
// ===============================

const tabs = document.querySelectorAll(".promotion-tab");
const promotionCards = document.querySelectorAll(".promotion-card");


// ===============================
// PROMOTION FILTER
// ===============================

tabs.forEach(tab => {

    tab.addEventListener("click", function () {

        const category = this.dataset.category;


        // Active tab
        tabs.forEach(item => {
            item.classList.remove("active");
        });

        this.classList.add("active");


        // Show / hide cards
        promotionCards.forEach(card => {

            const cardCategory =
                card.dataset.category;

            if (
                category === "all" ||
                cardCategory === category
            ) {

                card.style.display = "block";

            } else {

                card.style.display = "none";

            }

        });

    });

});
