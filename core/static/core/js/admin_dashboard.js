/* ============================================================
   SMART CAR RENTAL
   ADMIN DASHBOARD JAVASCRIPT
   Professional / Production-Ready Frontend Behavior
   ============================================================ */

(function () {
    "use strict";

    /* =========================================================
       DOM READY
       ========================================================= */

    document.addEventListener("DOMContentLoaded", function () {

        /* =====================================================
           ELEMENTS
           ===================================================== */

        const sidebar = document.getElementById("dashboardSidebar");
        const mobileMenuButton = document.getElementById("mobileMenuButton");

        const dashboardSearch = document.getElementById("dashboardSearch");
        const searchClear = document.getElementById("searchClear");
        const searchResults = document.getElementById("searchResults");
        const searchNoResults = document.getElementById("searchNoResults");

        const notificationButton =
            document.getElementById("notificationButton");

        const notificationDropdown =
            document.getElementById("notificationDropdown");

        const adminProfileButton =
            document.getElementById("adminProfileButton");

        const adminProfileDropdown =
            document.getElementById("adminProfileDropdown");


        /* =====================================================
           UTILITY FUNCTIONS
           ===================================================== */

        function isOpen(element) {
            return element && element.classList.contains("open");
        }


        function openElement(element) {
            if (!element) {
                return;
            }

            element.classList.add("open");
        }


        function closeElement(element) {
            if (!element) {
                return;
            }

            element.classList.remove("open");
        }


        function toggleElement(element) {
            if (!element) {
                return;
            }

            element.classList.toggle("open");
        }


        function setAriaExpanded(button, expanded) {
            if (!button) {
                return;
            }

            button.setAttribute(
                "aria-expanded",
                expanded ? "true" : "false"
            );
        }


        /* =====================================================
           SIDEBAR
           ===================================================== */

        function openSidebar() {
            if (!sidebar) {
                return;
            }

            sidebar.classList.add("open");

            if (mobileMenuButton) {
                setAriaExpanded(mobileMenuButton, true);
            }

            document.body.classList.add("sidebar-open");
        }


        function closeSidebar() {
            if (!sidebar) {
                return;
            }

            sidebar.classList.remove("open");

            if (mobileMenuButton) {
                setAriaExpanded(mobileMenuButton, false);
            }

            document.body.classList.remove("sidebar-open");
        }


        function toggleSidebar() {
            if (!sidebar) {
                return;
            }

            if (isOpen(sidebar)) {
                closeSidebar();
            } else {
                openSidebar();
            }
        }


        if (mobileMenuButton && sidebar) {
            mobileMenuButton.addEventListener("click", function (event) {
                event.stopPropagation();
                toggleSidebar();
            });
        }


        /* =====================================================
           CLOSE SIDEBAR WHEN CLICKING OUTSIDE
           ===================================================== */

        document.addEventListener("click", function (event) {

            if (!sidebar || !mobileMenuButton) {
                return;
            }

            const clickedInsideSidebar =
                sidebar.contains(event.target);

            const clickedMenuButton =
                mobileMenuButton.contains(event.target);

            if (
                window.innerWidth <= 1024 &&
                isOpen(sidebar) &&
                !clickedInsideSidebar &&
                !clickedMenuButton
            ) {
                closeSidebar();
            }
        });


        /* =====================================================
           RESET SIDEBAR ON DESKTOP
           ===================================================== */

        window.addEventListener("resize", function () {

            if (window.innerWidth > 1024) {
                closeSidebar();
            }

        });


        /* =====================================================
           DASHBOARD SEARCH
           ===================================================== */

        function getSearchItems() {

            if (!searchResults) {
                return [];
            }

            return Array.from(
                searchResults.querySelectorAll(
                    ".search-result-item"
                )
            );

        }


        function normalizeSearchText(value) {

            return String(value || "")
                .toLowerCase()
                .trim();

        }


        function performSearch() {

            if (!dashboardSearch || !searchResults) {
                return;
            }

            const query = normalizeSearchText(
                dashboardSearch.value
            );

            const items = getSearchItems();

            let visibleCount = 0;


            /* -----------------------------------------------
               EMPTY SEARCH
               ----------------------------------------------- */

            if (query === "") {

                items.forEach(function (item) {
                    item.hidden = false;
                    item.classList.remove("search-match");
                });

                if (searchNoResults) {
                    searchNoResults.hidden = true;
                }

                searchResults.classList.remove("has-results");

                return;
            }


            /* -----------------------------------------------
               FILTER RESULTS
               ----------------------------------------------- */

            items.forEach(function (item) {

                const searchData =
                    normalizeSearchText(
                        item.getAttribute("data-search")
                    );

                const itemText =
                    normalizeSearchText(
                        item.textContent
                    );

                const matches =
                    searchData.includes(query) ||
                    itemText.includes(query);


                if (matches) {

                    item.hidden = false;

                    item.classList.add(
                        "search-match"
                    );

                    visibleCount++;

                } else {

                    item.hidden = true;

                    item.classList.remove(
                        "search-match"
                    );

                }

            });


            /* -----------------------------------------------
               NO RESULTS
               ----------------------------------------------- */

            if (searchNoResults) {

                searchNoResults.hidden =
                    visibleCount !== 0;

            }


            searchResults.classList.add("has-results");
        }


        /* =====================================================
           OPEN SEARCH
           ===================================================== */

        function openSearch() {

            if (!dashboardSearch) {
                return;
            }

            dashboardSearch.focus();

            if (dashboardSearch.value.trim() !== "") {
                performSearch();
            }
        }


        /* =====================================================
           CLEAR SEARCH
           ===================================================== */

        function clearSearch() {

            if (!dashboardSearch) {
                return;
            }

            dashboardSearch.value = "";

            performSearch();

            dashboardSearch.focus();
        }


        if (dashboardSearch) {

            dashboardSearch.addEventListener(
                "input",
                performSearch
            );


            dashboardSearch.addEventListener(
                "focus",
                function () {

                    if (
                        dashboardSearch.value.trim() !== ""
                    ) {
                        performSearch();
                    }

                }
            );


            dashboardSearch.addEventListener(
                "keydown",
                function (event) {

                    /* Escape clears search */

                    if (event.key === "Escape") {

                        if (
                            dashboardSearch.value.trim() !== ""
                        ) {
                            clearSearch();
                        } else {
                            dashboardSearch.blur();
                        }

                    }

                }
            );
        }


        if (searchClear) {

            searchClear.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();
                    clearSearch();

                }
            );

        }


        /* =====================================================
           CTRL + K / CMD + K
           ===================================================== */

        document.addEventListener(
            "keydown",
            function (event) {

                const modifier =
                    event.ctrlKey || event.metaKey;


                if (
                    modifier &&
                    event.key.toLowerCase() === "k"
                ) {

                    event.preventDefault();

                    openSearch();

                }

            }
        );


        /* =====================================================
           SEARCH RESULT CLICK
           ===================================================== */

        if (searchResults) {

            searchResults.addEventListener(
                "click",
                function (event) {

                    const result =
                        event.target.closest(
                            ".search-result-item"
                        );

                    if (!result) {
                        return;
                    }

                    /*
                     * Let Django handle navigation normally.
                     * We only close the search UI.
                     */

                    searchResults.classList.remove(
                        "has-results"
                    );

                }
            );

        }


        /* =====================================================
           NOTIFICATION DROPDOWN
           ===================================================== */

        function openNotifications() {

            if (!notificationDropdown) {
                return;
            }

            closeProfileDropdown();

            openElement(notificationDropdown);

            setAriaExpanded(
                notificationButton,
                true
            );

        }


        function closeNotifications() {

            if (!notificationDropdown) {
                return;
            }

            closeElement(notificationDropdown);

            setAriaExpanded(
                notificationButton,
                false
            );

        }


        function toggleNotifications() {

            if (!notificationDropdown) {
                return;
            }

            if (isOpen(notificationDropdown)) {

                closeNotifications();

            } else {

                openNotifications();

            }

        }


        if (notificationButton) {

            notificationButton.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

                    toggleNotifications();

                }
            );

        }


        /* =====================================================
           ADMIN PROFILE DROPDOWN
           ===================================================== */

        function openProfileDropdown() {

            if (!adminProfileDropdown) {
                return;
            }

            closeNotifications();

            openElement(adminProfileDropdown);

            setAriaExpanded(
                adminProfileButton,
                true
            );

        }


        function closeProfileDropdown() {

            if (!adminProfileDropdown) {
                return;
            }

            closeElement(adminProfileDropdown);

            setAriaExpanded(
                adminProfileButton,
                false
            );

        }


        function toggleProfileDropdown() {

            if (!adminProfileDropdown) {
                return;
            }

            if (isOpen(adminProfileDropdown)) {

                closeProfileDropdown();

            } else {

                openProfileDropdown();

            }

        }


        if (adminProfileButton) {

            adminProfileButton.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

                    toggleProfileDropdown();

                }
            );

        }


        /* =====================================================
           GLOBAL OUTSIDE CLICK
           ===================================================== */

        document.addEventListener(
            "click",
            function (event) {

                /* ---------------------------------------------
                   Notifications
                   --------------------------------------------- */

                if (
                    notificationDropdown &&
                    notificationButton
                ) {

                    const clickedNotification =
                        notificationDropdown.contains(
                            event.target
                        );

                    const clickedNotificationButton =
                        notificationButton.contains(
                            event.target
                        );


                    if (
                        isOpen(notificationDropdown) &&
                        !clickedNotification &&
                        !clickedNotificationButton
                    ) {

                        closeNotifications();

                    }

                }


                /* ---------------------------------------------
                   Admin Profile
                   --------------------------------------------- */

                if (
                    adminProfileDropdown &&
                    adminProfileButton
                ) {

                    const clickedProfile =
                        adminProfileDropdown.contains(
                            event.target
                        );

                    const clickedProfileButton =
                        adminProfileButton.contains(
                            event.target
                        );


                    if (
                        isOpen(adminProfileDropdown) &&
                        !clickedProfile &&
                        !clickedProfileButton
                    ) {

                        closeProfileDropdown();

                    }

                }

            }
        );


        /* =====================================================
           ESCAPE KEY
           ===================================================== */

        document.addEventListener(
            "keydown",
            function (event) {

                if (event.key !== "Escape") {
                    return;
                }


                /* Close notifications */

                if (isOpen(notificationDropdown)) {
                    closeNotifications();
                }


                /* Close profile */

                if (isOpen(adminProfileDropdown)) {
                    closeProfileDropdown();
                }


                /* Close sidebar on mobile */

                if (
                    sidebar &&
                    window.innerWidth <= 1024 &&
                    isOpen(sidebar)
                ) {

                    closeSidebar();

                }

            }
        );


        /* =====================================================
           ACTIVE SIDEBAR NAVIGATION
           ===================================================== */

        function updateActiveNavigation() {

            const sidebarLinks =
                document.querySelectorAll(
                    ".sidebar-navigation .sidebar-link"
                );


            if (!sidebarLinks.length) {
                return;
            }


            const currentPath =
                window.location.pathname;


            sidebarLinks.forEach(function (link) {

                const href =
                    link.getAttribute("href");


                if (!href || href === "#") {
                    return;
                }


                try {

                    const linkURL =
                        new URL(
                            href,
                            window.location.origin
                        );


                    /*
                     * Exact match first.
                     */

                    const isExactMatch =
                        linkURL.pathname === currentPath;


                    /*
                     * For dashboard sections, allow
                     * nested URLs to remain active.
                     */

                    const isNestedMatch =
                        linkURL.pathname !== "/" &&
                        currentPath.startsWith(
                            linkURL.pathname
                        );


                    if (
                        isExactMatch ||
                        isNestedMatch
                    ) {

                        link.classList.add("active");

                    } else {

                        /*
                         * Do not remove the active class from
                         * explicitly marked dashboard link when
                         * Django is rendering the dashboard.
                         */

                        if (
                            currentPath !== "/" &&
                            linkURL.pathname !== currentPath
                        ) {

                            link.classList.remove(
                                "active"
                            );

                        }

                    }

                } catch (error) {

                    /*
                     * Invalid URL should not break
                     * the rest of dashboard JavaScript.
                     */

                    console.warn(
                        "Invalid navigation URL:",
                        href
                    );

                }

            });

        }


        updateActiveNavigation();


        /* =====================================================
           SEARCH VISIBILITY HELPERS
           ===================================================== */

        function updateSearchClearButton() {

            if (
                !dashboardSearch ||
                !searchClear
            ) {
                return;
            }

            const hasValue =
                dashboardSearch.value.trim() !== "";


            searchClear.classList.toggle(
                "visible",
                hasValue
            );

        }


        if (dashboardSearch) {

            dashboardSearch.addEventListener(
                "input",
                updateSearchClearButton
            );

        }


        updateSearchClearButton();


        /* =====================================================
           NOTIFICATION COUNT ACCESSIBILITY
           ===================================================== */

        if (
            notificationButton &&
            notificationDropdown
        ) {

            notificationButton.setAttribute(
                "aria-expanded",
                "false"
            );

        }


        /* =====================================================
           PROFILE ACCESSIBILITY
           ===================================================== */

        if (
            adminProfileButton &&
            adminProfileDropdown
        ) {

            adminProfileButton.setAttribute(
                "aria-expanded",
                "false"
            );

        }


        /* =====================================================
           INITIAL STATE
           ===================================================== */

        if (searchNoResults) {
            searchNoResults.hidden = true;
        }


        /* =====================================================
           DEBUG / DEVELOPMENT
           ===================================================== */

        console.info(
            "Smart Car Rental Admin Dashboard initialized."
        );

    });

})();