
document.addEventListener("DOMContentLoaded", function () {

    /* =====================================
       PROFILE DROPDOWN
    ===================================== */

    const profileButton = document.getElementById("profileButton");
    const profileDropdown = document.getElementById("profileDropdown");

    if (profileButton && profileDropdown) {

        profileButton.addEventListener("click", function (e) {
            e.stopPropagation();
            profileDropdown.classList.toggle("show");
        });

        document.addEventListener("click", function () {
            profileDropdown.classList.remove("show");
        });

        profileDropdown.addEventListener("click", function (e) {
            e.stopPropagation();
        });
    }


    /* =====================================
       MOBILE MENU
    ===================================== */

    const menuButton = document.querySelector(".menu-toggle");
    const navbar = document.querySelector("#main-navbar");

    if (menuButton && navbar) {

        menuButton.addEventListener("click", function () {
            navbar.classList.toggle("active");
        });
    }


    /* =====================================
       CONTACT VALIDATION
    ===================================== */

    const contactForm = document.querySelector("#contact-form");

    if (contactForm) {

        contactForm.addEventListener("submit", function (e) {

            const name = document.querySelector("#name");
            const email = document.querySelector("#email");
            const message = document.querySelector("#message");

            if (name && email && message) {

                if (name.value.trim().length < 2) {
                    alert("Name must contain at least 2 characters.");
                    e.preventDefault();
                    return;
                }

                const emailPattern =
                    /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

                if (!emailPattern.test(email.value)) {
                    alert("Enter a valid email address.");
                    e.preventDefault();
                    return;
                }

                if (message.value.trim().length < 10) {
                    alert("Message must contain at least 10 characters.");
                    e.preventDefault();
                    return;
                }
            }
        });
    }


    /* =====================================
       CAR SEARCH FILTER
    ===================================== */

    const carSearch = document.querySelector("#carSearch");
    const availabilityFilter =
        document.querySelector("#availabilityFilter");
    const priceFilter =
        document.querySelector("#priceFilter");
    const carGrid =
        document.querySelector(".car-grid");

    let carCards =
        Array.from(document.querySelectorAll(".car-card"));


    function filterCars() {

        let search =
            carSearch ?
            carSearch.value.toLowerCase() :
            "";

        let availability =
            availabilityFilter ?
            availabilityFilter.value :
            "all";


        carCards.forEach(function (card) {

            let name =
                card.dataset.name.toLowerCase();

            let status =
                card.dataset.status;

            let show = true;

            if (!name.includes(search)) {
                show = false;
            }

            if (
                availability !== "all" &&
                status !== availability
            ) {
                show = false;
            }

            card.style.display =
                show ? "block" : "none";
        });
    }


    function sortCars() {

        if (!carGrid || !priceFilter) {
            return;
        }

        let sorted = [...carCards];

        if (priceFilter.value === "low") {

            sorted.sort(function (a, b) {

                return (
                    Number(a.dataset.price) -
                    Number(b.dataset.price)
                );
            });
        }

        if (priceFilter.value === "high") {

            sorted.sort(function (a, b) {

                return (
                    Number(b.dataset.price) -
                    Number(a.dataset.price)
                );
            });
        }

        sorted.forEach(function (card) {
            carGrid.appendChild(card);
        });
    }


    if (carSearch) {
        carSearch.addEventListener(
            "keyup",
            filterCars
        );
    }

    if (availabilityFilter) {
        availabilityFilter.addEventListener(
            "change",
            filterCars
        );
    }

    if (priceFilter) {
        priceFilter.addEventListener(
            "change",
            sortCars
        );
    }


    /* =====================================
       BOOKING CALCULATOR
    ===================================== */

    const bookingForm =
        document.getElementById("bookingForm");

    const carSelect =
        document.querySelector("#car_type");

    const pickupDate =
        document.querySelector("#pickup_date");

    const dropoffDate =
        document.querySelector("#dropoff_date");


    const summaryCar =
        document.querySelector("#summary-car");

    const summaryPickup =
        document.querySelector("#summary-pickup");

    const summaryDropoff =
        document.querySelector("#summary-dropoff");

    const summaryDays =
        document.querySelector("#summary-days");

    const summaryPrice =
        document.querySelector("#summary-price");

    const summaryTotal =
        document.querySelector("#summary-total");


    /* =====================================
       DATE MINIMUM
    ===================================== */

    const today =
        new Date()
            .toISOString()
            .split("T")[0];


    if (pickupDate) {
        pickupDate.min = today;
    }

    if (dropoffDate) {
        dropoffDate.min = today;
    }


    if (pickupDate && dropoffDate) {

        pickupDate.addEventListener(
            "change",
            function () {

                if (pickupDate.value) {
                    dropoffDate.min =
                        pickupDate.value;
                }

                /*
                 * Do not automatically change
                 * the user's date.
                 *
                 * Django will display the
                 * correct validation message.
                 */
            }
        );
    }


    /* =====================================
       BOOKING CALCULATOR
    ===================================== */

    function calculateBooking() {

        if (!carSelect) {
            return;
        }

        let selected =
            carSelect.options[
                carSelect.selectedIndex
            ];


        if (!selected) {
            return;
        }


        let price =
            selected.dataset.price || 0;


        if (summaryCar) {

            summaryCar.textContent =
                selected.text;
        }


        if (summaryPickup) {

            summaryPickup.textContent =
                pickupDate && pickupDate.value
                    ? pickupDate.value
                    : "--";
        }


        if (summaryDropoff) {

            summaryDropoff.textContent =
                dropoffDate && dropoffDate.value
                    ? dropoffDate.value
                    : "--";
        }


        if (summaryPrice) {

            summaryPrice.textContent =
                price;
        }


        let days = 0;


        if (
            pickupDate &&
            dropoffDate &&
            pickupDate.value &&
            dropoffDate.value
        ) {

            let start =
                new Date(pickupDate.value);

            let end =
                new Date(dropoffDate.value);


            days =
                Math.ceil(
                    (end - start) /
                    (1000 * 60 * 60 * 24)
                );


            if (days < 0) {
                days = 0;
            }
        }


        if (summaryDays) {

            summaryDays.textContent =
                days;
        }


        let total =
            days * Number(price);


        if (summaryTotal) {

            summaryTotal.textContent =
                "ETB " +
                total.toLocaleString();
        }
    }


    if (carSelect) {

        carSelect.addEventListener(
            "change",
            calculateBooking
        );
    }

    if (pickupDate) {

        pickupDate.addEventListener(
            "change",
            calculateBooking
        );
    }

    if (dropoffDate) {

        dropoffDate.addEventListener(
            "change",
            calculateBooking
        );
    }


    calculateBooking();


    /* =====================================
       BOOKING CONFIRMATION MODAL
    ===================================== */

    const confirmBtn =
        document.getElementById(
            "confirmBookingBtn"
        );

    const bookingModal =
        document.getElementById(
            "bookingModal"
        );

    const closeModal =
        document.getElementById(
            "closeModal"
        );


    if (confirmBtn && bookingModal) {

        confirmBtn.addEventListener(
            "click",
            function (e) {

                /*
                 * Do NOT submit here.
                 * First show the confirmation modal.
                 */

                e.preventDefault();


                calculateBooking();


                const confirmCar =
                    document.getElementById(
                        "confirm-car"
                    );

                const confirmPickup =
                    document.getElementById(
                        "confirm-pickup"
                    );

                const confirmDropoff =
                    document.getElementById(
                        "confirm-dropoff"
                    );

                const confirmDays =
                    document.getElementById(
                        "confirm-days"
                    );

                const confirmTotal =
                    document.getElementById(
                        "confirm-total"
                    );


                if (confirmCar) {
                    confirmCar.textContent =
                        summaryCar
                            ? summaryCar.textContent
                            : "";
                }


                if (confirmPickup) {
                    confirmPickup.textContent =
                        summaryPickup
                            ? summaryPickup.textContent
                            : "";
                }


                if (confirmDropoff) {
                    confirmDropoff.textContent =
                        summaryDropoff
                            ? summaryDropoff.textContent
                            : "";
                }


                if (confirmDays) {
                    confirmDays.textContent =
                        summaryDays
                            ? summaryDays.textContent
                            : "0";
                }


                if (confirmTotal) {
                    confirmTotal.textContent =
                        summaryTotal
                            ? summaryTotal.textContent
                            : "ETB 0";
                }


                bookingModal.classList.add(
                    "active"
                );
            }
        );
    }


    /* =====================================
       CLOSE BOOKING MODAL
    ===================================== */

    if (closeModal && bookingModal) {

        closeModal.addEventListener(
            "click",
            function () {

                bookingModal.classList.remove(
                    "active"
                );
            }
        );
    }


    /* =====================================
       FINAL FORM SUBMISSION
    ===================================== */

    /*
     * IMPORTANT:
     *
     * The final confirmation button is:
     *
     * <button type="submit" form="bookingForm">
     *
     * We allow the browser to submit the
     * normal HTML form.
     *
     * Therefore Django receives the
     * {% csrf_token %} normally.
     */

});
