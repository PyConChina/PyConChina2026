document.addEventListener('DOMContentLoaded', function() {
    // 现代化导航栏功能
    const initModernNavbar = () => {
        const navbar = document.getElementById('navbar');
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const navMobile = document.getElementById('navMobile');
        const mobileClose = document.getElementById('mobileClose');
        const mobileOverlay = document.getElementById('mobileOverlay');
        const hamburger = mobileMenuToggle?.querySelector('.hamburger');

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateNavbarOnScroll);
                ticking = true;
            }
        });

        // 移动端菜单控制
        const openMobileMenu = () => {
            navMobile?.classList.add('active');
            mobileOverlay?.classList.add('active');
            hamburger?.classList.add('active');
            document.body.style.overflow = 'hidden';
        };

        const closeMobileMenu = () => {
            navMobile?.classList.remove('active');
            mobileOverlay?.classList.remove('active');
            hamburger?.classList.remove('active');
            document.body.style.overflow = '';
        };

        // 绑定事件
        mobileMenuToggle?.addEventListener('click', openMobileMenu);
        mobileClose?.addEventListener('click', closeMobileMenu);
        mobileOverlay?.addEventListener('click', closeMobileMenu);

        // 点击移动端导航链接时关闭菜单
        const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', closeMobileMenu);
        });

        // ESC键关闭移动端菜单
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeMobileMenu();
                closeLanguageDropdowns();
            }
        });

        // 语言/活动 下拉菜单功能
        const initLanguageDropdowns = () => {
            const languageDropdown = document.getElementById('languageDropdown');
            const languageDropdownMenu = document.getElementById('languageDropdownMenu');
            const activitiesDropdown = document.getElementById('activitiesDropdown');
            const activitiesDropdownMenu = document.getElementById('activitiesDropdownMenu');

            const openDropdown = (btn, menu) => {
                btn?.classList.add('active');
                menu?.classList.add('show');
            };

            const closeDropdown = (btn, menu) => {
                btn?.classList.remove('active');
                menu?.classList.remove('show');
            };

            const makeToggleHandler = (btn, menu) => (e) => {
                e.stopPropagation();
                if (!btn) return;
                const isActive = btn.classList.contains('active');
                // 先关闭所有
                closeAllDropdowns();
                if (!isActive) {
                    openDropdown(btn, menu);
                }
            };

            const closeAllDropdowns = () => {
                closeDropdown(languageDropdown, languageDropdownMenu);
                closeDropdown(activitiesDropdown, activitiesDropdownMenu);
            };

            // 全局暴露关闭方法（供 ESC/外部点击 调用）
            window.closeLanguageDropdowns = () => {
                closeAllDropdowns();
            };

            languageDropdown?.addEventListener('click', makeToggleHandler(languageDropdown, languageDropdownMenu));
            activitiesDropdown?.addEventListener('click', makeToggleHandler(activitiesDropdown, activitiesDropdownMenu));

            // 点击页面其他地方关闭下拉菜单
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.language-dropdown')) {
                    closeAllDropdowns();
                }
            });

            // 阻止下拉菜单内部点击事件冒泡
            languageDropdownMenu?.addEventListener('click', (e) => e.stopPropagation());
            activitiesDropdownMenu?.addEventListener('click', (e) => e.stopPropagation());
        };

        // 初始化语言/活动 下拉菜单
        initLanguageDropdowns();
    };

    // 初始化导航栏
    initModernNavbar();
});

// 卡片进入动画观察器
const observeCards = () => {
    const cards = document.querySelectorAll('.card, .staff-member, .search-result-item');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
};

// 平滑滚动到锚点
const initSmoothScroll = () => {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
};

// 添加浮动动画到特定元素
const addFloatingAnimation = () => {
    const floatingElements = document.querySelectorAll('.floating-element, .banner h1, .banner p');
    floatingElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.2}s`;
    });
};

// 搜索输入框焦点效果
const enhanceSearchInput = () => {
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('focused');
        });
    });
};

// 现代化按钮交互效果
const enhanceButtons = () => {
    const buttons = document.querySelectorAll('.page-button, .nav-link, .mobile-nav-link');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
};

// 页面加载动画
const pageLoadAnimation = () => {
    const elements = document.querySelectorAll('.page-title, .card, .banner');
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';

        setTimeout(() => {
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
};

// 初始化所有功能
const initializeEnhancements = () => {
    initModernNavbar();
    observeCards();
    initSmoothScroll();
    addFloatingAnimation();
    enhanceSearchInput();
    enhanceButtons();
    pageLoadAnimation();
};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', initializeEnhancements);
