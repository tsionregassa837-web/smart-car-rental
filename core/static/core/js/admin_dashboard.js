document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       ELEMENTS
    ====================================================== */

    const notificationButton =
        document.getElementById("notificationButton");

    const notificationDropdown =
        document.getElementById("notificationDropdown");

    const profileButton =
        document.getElementById("adminProfileButton") ||
        document.getElementById("profileButton");

    const profileDropdown =
        document.getElementById("adminProfileDropdown") ||
        document.getElementById("profileDropdown");

    const searchInput =
        document.getElementById("dashboardSearch") ||
        document.getElementById("searchInput");

    const searchResults =
        document.getElementById("searchResults");

    const searchClear =
        document.getElementById("searchClear");

    const mobileMenuButton =
        document.getElementById("mobileMenuButton");

    const sidebar =
        document.querySelector(".dashboard-sidebar");


    /* =====================================================
       HELPER FUNCTIONS
    ====================================================== */

    function closeNotificationDropdown() {
        if (notificationDropdown) {
            notificationDropdown.classList.remove("show");
            notificationDropdown.classList.remove("open");
        }

        if (notificationButton) {
            notificationButton.setAttribute(
                "aria-expanded",
                "false"
            );
        }
    }


    function closeProfileDropdown() {
        if (profileDropdown) {
            profileDropdown.classList.remove("show");
            profileDropdown.classList.remove("open");
        }

        if (profileButton) {
            profileButton.setAttribute(
                "aria-expanded",
                "false"
            );
        }
    }


    function closeSearchResults() {
        if (searchResults) {
            searchResults.classList.remove("show");
        }
    }


    function closeAllDropdowns() {
        closeNotificationDropdown();
        closeProfileDropdown();
        closeSearchResults();
    }


    /* =====================================================
       NOTIFICATIONS
    ====================================================== */

    if (notificationButton) {

        notificationButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                closeProfileDropdown();
                closeSearchResults();

                if (!notificationDropdown) {
                    window.location.href = "/booking-management/";
                    return;
                }

                const isOpen =
                    notificationDropdown.classList.contains("show") ||
                    notificationDropdown.classList.contains("open");

                if (isOpen) {

                    closeNotificationDropdown();

                } else {

                    notificationDropdown.classList.add("show");

                    notificationButton.setAttribute(
                        "aria-expanded",
                        "true"
                    );
                }
            }
        );
    }


    /* =====================================================
       ADMIN PROFILE
    ====================================================== */

    if (profileButton) {

        profileButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                closeNotificationDropdown();
                closeSearchResults();

                if (!profileDropdown) {
                    return;
                }

                const isOpen =
                    profileDropdown.classList.contains("show") ||
                    profileDropdown.classList.contains("open");

                if (isOpen) {

                    closeProfileDropdown();

                } else {

                    profileDropdown.classList.add("show");
                    profileDropdown.classList.add("open");

                    profileButton.setAttribute(
                        "aria-expanded",
                        "true"
                    );
                }
            }
        );
    }


    /* =====================================================
       CLOSE DROPDOWNS WHEN CLICKING OUTSIDE
    ====================================================== */

    document.addEventListener(
        "click",
        function (event) {

            if (
                notificationDropdown &&
                notificationButton &&
                !notificationDropdown.contains(event.target) &&
                !notificationButton.contains(event.target)
            ) {
                closeNotificationDropdown();
            }


            if (
                profileDropdown &&
                profileButton &&
                !profileDropdown.contains(event.target) &&
                !profileButton.contains(event.target)
            ) {
                closeProfileDropdown();
            }


            if (
                searchResults &&
                searchInput &&
                !searchResults.contains(event.target) &&
                !searchInput.contains(event.target)
            ) {
                closeSearchResults();
            }
        }
    );


    /* =====================================================
       SEARCH DATA
    ====================================================== */

    const searchableItems = [

        {
            title: "Dashboard",
            type: "Navigation",
            icon: "▦",
            url: "/admin-dashboard/"
        },

        {
            title: "Fleet Management",
            type: "Navigation",
            icon: "🚗",
            url: "/fleet-management/"
        },

        {
            title: "Booking Management",
            type: "Navigation",
            icon: "📋",
            url: "/booking-management/"
        },

        {
            title: "Customer Management",
            type: "Navigation",
            icon: "👥",
            url: "/customer-management/"
        },

        {
            title: "Payment Management",
            type: "Navigation",
            icon: "💳",
            url: "/payment-management/"
        },

        {
            title: "Reports",
            type: "Navigation",
            icon: "📈",
            url: "/reports/"
        },

        {
            title: "Settings",
            type: "Navigation",
            icon: "⚙️",
            url: "/admin-settings/"
        }
    ];


    /* =====================================================
       ESCAPE HTML
    ====================================================== */

    function escapeHTML(value) {

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    /* =====================================================
       RENDER SEARCH RESULTS
    ====================================================== */

    function renderSearchResults(query) {

        if (!searchResults) {
            return;
        }

        const normalizedQuery =
            String(query || "")
                .trim()
                .toLowerCase();


        if (!normalizedQuery) {

            searchResults.innerHTML = "";
            searchResults.classList.remove("show");

            return;
        }


        const results =
            searchableItems.filter(function (item) {

                return (
                    item.title
                        .toLowerCase()
                        .includes(normalizedQuery)

                    ||

                    item.type
                        .toLowerCase()
                        .includes(normalizedQuery)
                );
            });


        searchResults.innerHTML = "";


        if (results.length === 0) {

            const empty =
                document.createElement("div");

            empty.className =
                "search-no-results";

            empty.textContent =
                "No dashboard section found.";

            searchResults.appendChild(empty);

        } else {

            results.forEach(function (item) {

                const link =
                    document.createElement("a");

                link.className =
                    "search-result-item";

                link.href =
                    item.url;

                link.innerHTML = `
                    <span class="search-result-icon">
                        ${escapeHTML(item.icon)}
                    </span>

                    <span>
                        <strong>
                            ${escapeHTML(item.title)}
                        </strong>

                        <small>
                            ${escapeHTML(item.type)}
                        </small>
                    </span>
                `;

                searchResults.appendChild(link);
            });
        }


        searchResults.classList.add("show");
    }


    /* =====================================================
       SEARCH INPUT
    ====================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                renderSearchResults(
                    searchInput.value
                );
            }
        );


        searchInput.addEventListener(
            "focus",
            function () {

                if (
                    searchInput.value.trim()
                ) {

                    renderSearchResults(
                        searchInput.value
                    );
                }
            }
        );
    }


    /* =====================================================
       SEARCH CLEAR BUTTON
    ====================================================== */

    if (searchClear && searchInput) {

        searchClear.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                searchInput.value = "";

                closeSearchResults();

                searchInput.focus();
            }
        );
    }


    /* =====================================================
       CTRL + K / CMD + K
    ====================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                (event.ctrlKey || event.metaKey) &&
                event.key.toLowerCase() === "k"
            ) {

                event.preventDefault();

                if (searchInput) {

                    searchInput.focus();
                    searchInput.select();
                }
            }
        }
    );


    /* =====================================================
       ESCAPE KEY
    ====================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeAllDropdowns();


                if (sidebar) {

                    sidebar.classList.remove(
                        "mobile-open"
                    );
                }


                if (mobileMenuButton) {

                    mobileMenuButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );
                }
            }
        }
    );


    /* =====================================================
       MOBILE SIDEBAR
    ====================================================== */

    if (mobileMenuButton && sidebar) {

        mobileMenuButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                const isOpen =
                    sidebar.classList.toggle(
                        "mobile-open"
                    );

                mobileMenuButton.setAttribute(
                    "aria-expanded",
                    isOpen ? "true" : "false"
                );
            }
        );
    }


    /* =====================================================
       CLOSE MOBILE SIDEBAR AFTER NAVIGATION
    ====================================================== */

    if (sidebar) {

        const sidebarLinks =
            sidebar.querySelectorAll(
                "a.sidebar-link"
            );


        sidebarLinks.forEach(
            function (link) {

                link.addEventListener(
                    "click",
                    function () {

                        if (
                            window.innerWidth <= 750
                        ) {

                            sidebar.classList.remove(
                                "mobile-open"
                            );


                            if (mobileMenuButton) {

                                mobileMenuButton.setAttribute(
                                    "aria-expanded",
                                    "false"
                                );
                            }
                        }
                    }
                );
            }
        );
    }


    /* =====================================================
       CLOSE MOBILE SIDEBAR OUTSIDE
    ====================================================== */

    document.addEventListener(
        "click",
        function (event) {

            if (
                window.innerWidth <= 750 &&
                sidebar &&
                mobileMenuButton &&
                sidebar.classList.contains("mobile-open") &&
                !sidebar.contains(event.target) &&
                !mobileMenuButton.contains(event.target)
            ) {

                sidebar.classList.remove(
                    "mobile-open"
                );


                mobileMenuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );
            }
        }
    );


    /* =====================================================
       DJANGO CHART DATA
    ====================================================== */

    function getJSONData(id, fallback) {

        const element =
            document.getElementById(id);

        if (!element) {
            return fallback;
        }


        try {

            return JSON.parse(
                element.textContent
            );

        } catch (error) {

            console.error(
                "Unable to read dashboard data:",
                id,
                error
            );

            return fallback;
        }
    }


    const bookingStatusData = {

        pending:
            Number(
                getJSONData(
                    "pendingBookingsData",
                    0
                )
            ) || 0,

        approved:
            Number(
                getJSONData(
                    "approvedBookingsData",
                    0
                )
            ) || 0,

        active:
            Number(
                getJSONData(
                    "activeRentalsData",
                    0
                )
            ) || 0,

        completed:
            Number(
                getJSONData(
                    "completedBookingsData",
                    0
                )
            ) || 0,

        cancelled:
            Number(
                getJSONData(
                    "cancelledBookingsData",
                    0
                )
            ) || 0
    };


    const fleetStatusData = {

        available:
            Number(
                getJSONData(
                    "availableCarsData",
                    0
                )
            ) || 0,

        rented:
            Number(
                getJSONData(
                    "rentedCarsData",
                    0
                )
            ) || 0,

        maintenance:
            Number(
                getJSONData(
                    "maintenanceCarsData",
                    0
                )
            ) || 0,

        inactive:
            Number(
                getJSONData(
                    "inactiveCarsData",
                    0
                )
            ) || 0
    };


    /* =====================================================
       BOOKING CHART
    ====================================================== */

    const bookingCanvas =
        document.getElementById(
            "bookingChart"
        );


    if (
        bookingCanvas &&
        typeof Chart !== "undefined"
    ) {

        const existingBookingChart =
            Chart.getChart(bookingCanvas);


        if (existingBookingChart) {
            existingBookingChart.destroy();
        }


        new Chart(
            bookingCanvas,
            {
                type: "doughnut",

                data: {

                    labels: [
                        "Pending",
                        "Approved",
                        "Active",
                        "Completed",
                        "Cancelled"
                    ],

                    datasets: [
                        {
                            label: "Bookings",

                            data: [
                                bookingStatusData.pending,
                                bookingStatusData.approved,
                                bookingStatusData.active,
                                bookingStatusData.completed,
                                bookingStatusData.cancelled
                            ],

                            borderWidth: 0,
                            hoverOffset: 6
                        }
                    ]
                },

                options: {

                    responsive: true,
                    maintainAspectRatio: false,

                    cutout: "68%",

                    plugins: {

                        legend: {

                            position: "bottom",

                            labels: {

                                usePointStyle: true,
                                padding: 18,

                                font: {
                                    size: 11
                                }
                            }
                        },

                        tooltip: {
                            enabled: true
                        }
                    }
                }
            }
        );
    }


    /* =====================================================
       FLEET CHART
    ====================================================== */

    const fleetCanvas =
        document.getElementById(
            "fleetChart"
        );


    if (
        fleetCanvas &&
        typeof Chart !== "undefined"
    ) {

        const existingFleetChart =
            Chart.getChart(fleetCanvas);


        if (existingFleetChart) {
            existingFleetChart.destroy();
        }


        new Chart(
            fleetCanvas,
            {
                type: "doughnut",

                data: {

                    labels: [
                        "Available",
                        "Rented",
                        "Maintenance",
                        "Inactive"
                    ],

                    datasets: [
                        {
                            label: "Fleet",

                            data: [
                                fleetStatusData.available,
                                fleetStatusData.rented,
                                fleetStatusData.maintenance,
                                fleetStatusData.inactive
                            ],

                            borderWidth: 0,
                            hoverOffset: 6
                        }
                    ]
                },

                options: {

                    responsive: true,
                    maintainAspectRatio: false,

                    cutout: "68%",

                    plugins: {

                        legend: {

                            position: "bottom",

                            labels: {

                                usePointStyle: true,
                                padding: 18,

                                font: {
                                    size: 11
                                }
                            }
                        },

                        tooltip: {
                            enabled: true
                        }
                    }
                }
            }
        );
    }


    /* =====================================================
       WINDOW RESIZE
    ====================================================== */

    window.addEventListener(
        "resize",
        function () {

            if (
                window.innerWidth > 750 &&
                sidebar
            ) {

                sidebar.classList.remove(
                    "mobile-open"
                );


                if (mobileMenuButton) {

                    mobileMenuButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );
                }
            }
        }
    );


    /* =====================================================
       INITIAL ACCESSIBILITY STATE
    ====================================================== */

    if (profileButton) {

        profileButton.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    if (notificationButton) {

        notificationButton.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    if (mobileMenuButton) {

        mobileMenuButton.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    /* =====================================================
       DEBUG
    ====================================================== */

    console.log(
        "Smart Car Rental Admin Dashboard JS loaded successfully."
    );

});