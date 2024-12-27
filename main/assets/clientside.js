if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    animate_notifications: function(children) {
        if (children) {
            children.forEach((child) => {
                if (child && child.props && child.props.id) {
                    const el = document.getElementById(child.props.id.index);
                    if (el) {
                        el.style.opacity = '0';
                        el.style.transform = 'translateY(-100%)';
                        setTimeout(() => {
                            el.style.opacity = '1';
                            el.style.transform = 'translateY(0)';
                        }, 100);
                        
                        setTimeout(() => {
                            el.style.opacity = '0';
                            el.style.transform = 'translateY(-100%)';
                            setTimeout(() => {
                                if (el.parentNode) {
                                    el.parentNode.removeChild(el);
                                }
                            }, 500);
                        }, 5000);
                    }
                }
            });
        }
        return window.dash_clientside.no_update;
    }
};
