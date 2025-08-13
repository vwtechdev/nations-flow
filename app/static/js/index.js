'use strict'

$(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alert messages after 15 seconds
    $('.alert').delay(15000).fadeOut(500);
    
    // Add smooth transitions to form elements
    $('.form-control, .form-select').on('focus', function() {
        $(this).addClass('shadow-sm');
    }).on('blur', function() {
        $(this).removeClass('shadow-sm');
    });
    
    // Função para identificar se um formulário é de filtro
    function isFilterForm(form) {
        const formId = form.id || '';
        const formMethod = form.method || '';
        const formAction = form.action || '';
        const formClass = form.className || '';
        
        // Verificar se é um formulário de filtro baseado em vários critérios
        return formId.includes('Filter') || 
               formId.includes('filter') || 
               formId.includes('Search') || 
               formId.includes('search') ||
               formMethod.toLowerCase() === 'get' ||
               formAction.includes('filter') ||
               formAction.includes('search') ||
               formClass.includes('filter') ||
               formClass.includes('search');
    }
    
    // Add loading state to submit buttons
    $('form').each(function() {
        if (!isFilterForm(this)) {
            $(this).on('submit', function() {
                const submitBtn = $(this).find('button[type="submit"]');
                if (submitBtn.length > 0) {
                    const originalText = submitBtn.html();
                    
                    submitBtn.prop('disabled', true);
                    submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Salvando...');
                    
                    // Re-enable button after 10 seconds if form submission fails
                    setTimeout(function() {
                        submitBtn.prop('disabled', false);
                        submitBtn.html(originalText);
                    }, 10000);
                }
            });
        }
    });
    
    // Add enter key support for form submission
    $('input, select').each(function() {
        const form = $(this).closest('form')[0];
        if (!form || !isFilterForm(form)) {
            $(this).on('keypress', function(e) {
                if (e.which === 13) { // Enter key
                    e.preventDefault();
                    $(this).closest('form').submit();
                }
            });
        }
    });
    
    // Add table row hover effects
    $('.table tbody tr').hover(
        function() {
            $(this).addClass('table-hover');
        },
        function() {
            $(this).removeClass('table-hover');
        }
    );
    
    // Add smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 500);
        }
    });
    
    // Add responsive table wrapper
    $('.table').wrap('<div class="table-responsive"></div>');
    
    // Add form validation feedback
    $('.form-control').on('input', function() {
        if (this.checkValidity()) {
            $(this).removeClass('is-invalid').addClass('is-valid');
        } else {
            $(this).removeClass('is-valid').addClass('is-invalid');
        }
    });
    
    // Add card hover effects
    $('.card').hover(
        function() {
            $(this).addClass('shadow-lg');
        },
        function() {
            $(this).removeClass('shadow-lg');
        }
    );
    
    // Sidebar and Navigation Drawer functionality
    const sidebar = $('#sidebar');
    const navigationDrawer = $('#navigationDrawer');
    const mainContent = $('#mainContent');
    const sidebarToggle = $('#sidebarToggle');
    const actionBarMenuBtn = $('#actionBarMenuBtn');
    const navigationDrawerOverlay = $('#navigationDrawerOverlay');
    const navigationDrawerClose = $('#navigationDrawerClose');
    
    // Check if sidebar exists
    if (sidebar.length > 0) {
        console.log('Setting up sidebar functionality');
        
        // Function to toggle mobile navigation drawer
        function toggleNavigationDrawer() {
            navigationDrawer.toggleClass('show');
            navigationDrawerOverlay.toggleClass('show');
            $('body').toggleClass('drawer-open');
            
            // Update action bar menu button icon
            const actionBarIcon = actionBarMenuBtn.find('i');
            if (navigationDrawer.hasClass('show')) {
                actionBarIcon.removeClass('bi-list').addClass('bi-x');
            } else {
                actionBarIcon.removeClass('bi-x').addClass('bi-list');
            }
        }
        
        // Function to close mobile navigation drawer
        function closeNavigationDrawer() {
            navigationDrawer.removeClass('show');
            navigationDrawerOverlay.removeClass('show');
            $('body').removeClass('drawer-open');
            
            // Update action bar menu button icon
            const actionBarIcon = actionBarMenuBtn.find('i');
            actionBarIcon.removeClass('bi-x').addClass('bi-list');
        }
        
        // Action bar menu button functionality
        if (actionBarMenuBtn.length > 0) {
            actionBarMenuBtn.on('click', function(e) {
                e.preventDefault();
                toggleNavigationDrawer();
            });
        }
        
        // Navigation drawer close button functionality
        if (navigationDrawerClose.length > 0) {
            navigationDrawerClose.on('click', function(e) {
                e.preventDefault();
                closeNavigationDrawer();
            });
        }
        
        // Close navigation drawer when clicking overlay
        navigationDrawerOverlay.on('click', function() {
            closeNavigationDrawer();
        });
        
        // Close navigation drawer when clicking on a link (mobile)
        $(document).on('click', '.navigation-drawer-link', function() {
            if ($(window).width() <= 768) {
                closeNavigationDrawer();
            }
        });
        
        // Toggle sidebar (desktop)
        sidebarToggle.on('click', function(e) {
            e.preventDefault();
            sidebar.toggleClass('collapsed');
            mainContent.toggleClass('expanded');
            
            // Save state to localStorage
            const isCollapsed = sidebar.hasClass('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
            
            // Update toggle button icon
            const toggleIcon = $(this).find('i');
            if (isCollapsed) {
                toggleIcon.removeClass('bi-list').addClass('bi-chevron-right');
            } else {
                toggleIcon.removeClass('bi-chevron-right').addClass('bi-list');
            }
            
            console.log('Sidebar toggled:', isCollapsed ? 'collapsed' : 'expanded');
        });
        
        // Load sidebar state from localStorage
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.addClass('collapsed');
            mainContent.addClass('expanded');
            // Update toggle button icon
            const toggleIcon = sidebarToggle.find('i');
            toggleIcon.removeClass('bi-list').addClass('bi-chevron-right');
        }
        
        // Load active link from localStorage as fallback
        const savedActiveLink = localStorage.getItem('activeSidebarLink');
        if (savedActiveLink && !$('.sidebar-link.active').length) {
            const savedLink = $(`.sidebar-link[href="${savedActiveLink}"]`);
            if (savedLink.length > 0) {
                savedLink.addClass('active');
                console.log('Active link loaded from localStorage:', savedActiveLink);
            }
        }
        
        // Mobile sidebar toggle
        if ($(window).width() <= 768) {
            sidebar.addClass('collapsed');
            mainContent.addClass('expanded');
            // Update toggle button icon
            const toggleIcon = sidebarToggle.find('i');
            toggleIcon.removeClass('bi-list').addClass('bi-chevron-right');
            
            // Show action bar on mobile
            $('#mobileActionBar').show();
        } else {
            // Hide action bar on desktop
            $('#mobileActionBar').hide();
        }
        
        // Handle window resize
        $(window).on('resize', function() {
            if ($(window).width() <= 768) {
                sidebar.addClass('collapsed');
                mainContent.addClass('expanded');
                // Update toggle button icon
                const toggleIcon = sidebarToggle.find('i');
                toggleIcon.removeClass('bi-list').addClass('bi-chevron-right');
                
                // Close navigation drawer if open
                if (navigationDrawer.hasClass('show')) {
                    closeNavigationDrawer();
                }
                
                // Ensure action bar is visible on mobile
                $('#mobileActionBar').show();
            } else {
                // On desktop, remove mobile-specific classes
                navigationDrawer.removeClass('show');
                navigationDrawerOverlay.removeClass('show');
                $('body').removeClass('drawer-open');
                
                // Reset action bar menu button icon
                if (actionBarMenuBtn.length > 0) {
                    const actionBarIcon = actionBarMenuBtn.find('i');
                    actionBarIcon.removeClass('bi-x').addClass('bi-list');
                }
                
                // Hide action bar on desktop
                $('#mobileActionBar').hide();
            }
        });
        
        // Set active link based on current URL
        const currentPath = window.location.pathname;
        console.log('Current path:', currentPath);
        
        // Remove any existing active classes
        $('.sidebar-link, .navigation-drawer-link').removeClass('active');
        
        // Define URL patterns for each section
        const urlPatterns = {
            'index': ['/'],
            'transaction_list': ['/transactions/'],
            'category_list': ['/categories/'],
            'field_list': ['/fields/'],
            'church_list': ['/churches/'],
            'user_list': ['/users/']
        };
        
        // Check each pattern and set active class
        let activeFound = false;
        for (const [section, patterns] of Object.entries(urlPatterns)) {
            for (const pattern of patterns) {
                // Special handling for dashboard (root path)
                if (pattern === '/' && currentPath === '/') {
                    const activeSidebarLink = $(`.sidebar-link[href="/"]`);
                    const activeDrawerLink = $(`.navigation-drawer-link[href="/"]`);
                    if (activeSidebarLink.length > 0) {
                        activeSidebarLink.addClass('active');
                        activeFound = true;
                        console.log('Active link set for dashboard (root) - sidebar');
                    }
                    if (activeDrawerLink.length > 0) {
                        activeDrawerLink.addClass('active');
                        activeFound = true;
                        console.log('Active link set for dashboard (root) - drawer');
                    }
                    break;
                }
                // For other patterns, check if current path starts with the pattern
                else if (pattern !== '/' && currentPath.startsWith(pattern)) {
                    const activeSidebarLink = $(`.sidebar-link[href*="${pattern}"]`);
                    const activeDrawerLink = $(`.navigation-drawer-link[href*="${pattern}"]`);
                    if (activeSidebarLink.length > 0) {
                        activeSidebarLink.addClass('active');
                        activeFound = true;
                        console.log('Active link set for:', section, 'pattern:', pattern, '- sidebar');
                    }
                    if (activeDrawerLink.length > 0) {
                        activeDrawerLink.addClass('active');
                        activeFound = true;
                        console.log('Active link set for:', section, 'pattern:', pattern, '- drawer');
                    }
                    break;
                }
            }
            if (activeFound) break;
        }
        
        // Fallback: if no pattern matches, try to match by URL name
        if (!activeFound) {
            $('.sidebar-link, .navigation-drawer-link').each(function() {
                const linkPath = $(this).attr('href');
                if (linkPath && linkPath !== '/') { // Skip dashboard link in fallback
                    // Extract the main part of the URL (first segment after domain)
                    const linkSegments = linkPath.split('/').filter(segment => segment);
                    const currentSegments = currentPath.split('/').filter(segment => segment);
                    
                    if (linkSegments.length > 0 && currentSegments.length > 0) {
                        if (linkSegments[0] === currentSegments[0]) {
                            $(this).addClass('active');
                            console.log('Active link set by segment match:', linkSegments[0]);
                            activeFound = true;
                            return false; // break the loop
                        }
                    }
                }
            });
        }
        
        // If still no active link found and we're on the root, set dashboard as active
        if (!activeFound && currentPath === '/') {
            $('.sidebar-link[href="/"], .navigation-drawer-link[href="/"]').addClass('active');
            console.log('Active link set for dashboard (root) - fallback');
        }
        
        // Save active link to localStorage for persistence
        const activeLink = $('.sidebar-link.active, .navigation-drawer-link.active');
        if (activeLink.length > 0) {
            const activeHref = activeLink.first().attr('href');
            localStorage.setItem('activeSidebarLink', activeHref);
            console.log('Active link saved to localStorage:', activeHref);
        }
        
        // Ensure only one link is active at a time per navigation type
        const activeSidebarLinks = $('.sidebar-link.active');
        const activeDrawerLinks = $('.navigation-drawer-link.active');
        if (activeSidebarLinks.length > 1) {
            console.warn('Multiple active sidebar links found, keeping only the first one');
            activeSidebarLinks.not(':first').removeClass('active');
        }
        if (activeDrawerLinks.length > 1) {
            console.warn('Multiple active drawer links found, keeping only the first one');
            activeDrawerLinks.not(':first').removeClass('active');
        }
        
        // Add keyboard shortcut for sidebar toggle (Ctrl/Cmd + B)
        $(document).on('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                sidebarToggle.click();
            }
        });
        
        // Update active link when clicking on sidebar or navigation drawer links
        $('.sidebar-link, .navigation-drawer-link').on('click', function() {
            // Remove active class from all links of the same type
            const isSidebarLink = $(this).hasClass('sidebar-link');
            const isDrawerLink = $(this).hasClass('navigation-drawer-link');
            
            if (isSidebarLink) {
                $('.sidebar-link').removeClass('active');
            }
            if (isDrawerLink) {
                $('.navigation-drawer-link').removeClass('active');
            }
            
            // Add active class to clicked link
            $(this).addClass('active');
            
            // Save to localStorage
            const href = $(this).attr('href');
            localStorage.setItem('activeSidebarLink', href);
            console.log('Active link updated on click:', href);
        });
    }
    
    // Floating Action Button functionality
    const floatingBtn = $('.floating-action-btn');
    const floatingMenu = $('.floating-action-menu');
    
    console.log('Floating button found:', floatingBtn.length);
    console.log('Floating menu found:', floatingMenu.length);
    
    if (floatingBtn.length > 0) {
        console.log('Setting up floating button events');
        
        floatingBtn.on('click', function(e) {
            console.log('Floating button clicked');
            
            // Se é um link (tesoureiro), não fazer nada - deixar o link funcionar
            if ($(this).is('a')) {
                console.log('Floating button is a link - allowing navigation');
                return;
            }
            
            // Se é um botão (administrador), controlar o bottom sheet
            e.preventDefault();
            
            // Verificar se é o botão de administrador
            if ($(this).attr('id') === 'adminFab') {
                // A funcionalidade do bottom sheet será tratada separadamente
                console.log('Admin FAB clicked - bottom sheet will be handled separately');
                return;
            } else {
                // Fallback para o menu flutuante antigo (se ainda existir)
                floatingMenu.toggleClass('show');
                
                // Change icon based on menu state
                const icon = $(this).find('i');
                if (floatingMenu.hasClass('show')) {
                    icon.removeClass('bi-plus').addClass('bi-x');
                    console.log('Menu opened');
                } else {
                    icon.removeClass('bi-x').addClass('bi-plus');
                    console.log('Menu closed');
                }
            }
        });
        
        // Bottom Sheet functionality
        const bottomSheet = $('#adminBottomSheet');
        const bottomSheetOverlay = $('#bottomSheetOverlay');
        const bottomSheetClose = $('#bottomSheetClose');
        const adminFab = $('#adminFab');
        
        if (bottomSheet.length > 0) {
            console.log('Setting up bottom sheet events');
            
            // Função para abrir o bottom sheet
            function openBottomSheet() {
                console.log('Opening bottom sheet...');
                bottomSheet.addClass('show');
                const icon = adminFab.find('i');
                icon.removeClass('bi-plus').addClass('bi-x');
                console.log('Bottom sheet opened');
            }
            
            // Função para fechar o bottom sheet
            function closeBottomSheet() {
                console.log('Closing bottom sheet...');
                
                // Primeiro, animar o fechamento
                const content = bottomSheet.find('.bottom-sheet-content');
                content.css('transform', 'translateY(100%)');
                
                // Aguardar a animação terminar antes de esconder
                setTimeout(() => {
                    bottomSheet.removeClass('show');
                    const icon = adminFab.find('i');
                    icon.removeClass('bi-x').addClass('bi-plus');
                    console.log('Bottom sheet closed');
                }, 300);
            }
            
            // Evento de clique no FAB do administrador
            adminFab.off('click').on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                openBottomSheet();
            });
            
            // Close bottom sheet when clicking overlay
            bottomSheetOverlay.on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeBottomSheet();
            });
            
            // Close bottom sheet when clicking close button
            bottomSheetClose.on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeBottomSheet();
            });
            
            // Close bottom sheet on escape key
            $(document).on('keydown', function(e) {
                if (e.key === 'Escape' && bottomSheet.hasClass('show')) {
                    e.preventDefault();
                    closeBottomSheet();
                }
            });
            
            // Swipe down to close (touch devices)
            let startY = 0;
            let currentY = 0;
            let isDragging = false;
            
            bottomSheet.on('touchstart', function(e) {
                startY = e.touches[0].clientY;
                isDragging = true;
            });
            
            bottomSheet.on('touchmove', function(e) {
                if (!isDragging) return;
                
                currentY = e.touches[0].clientY;
                const deltaY = currentY - startY;
                
                if (deltaY > 0) { // Swiping down
                    const translateY = Math.min(deltaY, 100);
                    bottomSheet.find('.bottom-sheet-content').css('transform', `translateY(${translateY}px)`);
                }
            });
            
            bottomSheet.on('touchend', function(e) {
                if (!isDragging) return;
                
                const deltaY = currentY - startY;
                if (deltaY > 100) { // Swipe down threshold
                    closeBottomSheet();
                } else {
                    // Reset position
                    bottomSheet.find('.bottom-sheet-content').css('transform', 'translateY(0)');
                }
                
                isDragging = false;
            });
            
            // Close bottom sheet when clicking outside
            $(document).on('click', function(e) {
                if (bottomSheet.hasClass('show') && 
                    !$(e.target).closest('.floating-action-btn, .bottom-sheet-content').length) {
                    closeBottomSheet();
                }
            });
        }
        
        // Close menu when clicking outside (fallback para menu antigo)
        $(document).on('click', function(e) {
            if (!$(e.target).closest('.floating-action-btn, .floating-action-menu').length) {
                floatingMenu.removeClass('show');
                floatingBtn.find('i').removeClass('bi-x').addClass('bi-plus');
            }
        });
        
        // Close menu on escape key (fallback para menu antigo)
        $(document).on('keydown', function(e) {
            if (e.key === 'Escape') {
                floatingMenu.removeClass('show');
                floatingBtn.find('i').removeClass('bi-x').addClass('bi-plus');
            }
        });
    } else {
        console.log('No floating button found on page');
    }
});
