if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    animate_notifications: function(children) {
        if (children) {
            children.forEach((child, index) => {
                if (child && child.props && child.props.id) {
                    const el = document.getElementById(JSON.stringify(child.props.id));
                    if (el) {
                        // Initial state
                        el.style.opacity = '0';
                        el.style.transform = 'translateX(100%)';
                        
                        // Fade in and slide in
                        setTimeout(() => {
                            el.style.transition = 'opacity 0.5s, transform 0.5s';
                            el.style.opacity = '1';
                            el.style.transform = 'translateX(0)';
                        }, 100 * index);  // Stagger the animations
                        
                        // Fade out and slide out after 4.5 seconds
                        setTimeout(() => {
                            el.style.opacity = '0';
                            el.style.transform = 'translateX(100%)';
                            
                            // Remove the notification after the animation
                            setTimeout(() => {
                                el.remove();
                            }, 500);
                        }, 4500 + 100 * index);
                    }
                }
            });
        }
        return window.dash_clientside.no_update;
    },

    update_chevron: function(is_open, id) {
        console.log('update_chevron called with:', is_open, id);
        if (id && id.index !== undefined) {
            const collectionToggle = document.querySelector(`[id$='"index":${id.index}}']`);
            console.log('collectionToggle:', collectionToggle);
            if (collectionToggle) {
                const collectionItem = collectionToggle.closest('.collection-item');
                console.log('collectionItem:', collectionItem);
                if (collectionItem) {
                    if (is_open) {
                        collectionItem.classList.add('expanded');
                    } else {
                        collectionItem.classList.remove('expanded');
                    }
                }
            }
        }
        return window.dash_clientside.no_update;
    },
};
