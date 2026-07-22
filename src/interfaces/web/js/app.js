const API_BASE = '';
let activeClientId = null;

// --- UI Helpers ---
function notify(message, type = 'info') {
    console.log(`[Notify] ${type}: ${message}`);
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    const colors = {
        info: 'bg-slate-800 text-white',
        success: 'bg-green-600 text-white',
        error: 'bg-red-600 text-white',
        warning: 'bg-yellow-500 text-slate-900'
    };
    const icons = {
        info: 'fa-circle-info',
        success: 'fa-circle-check',
        error: 'fa-circle-exclamation',
        warning: 'fa-triangle-exclamation'
    };

    toast.className = `${colors[type]} px-4 py-3 rounded-lg shadow-lg flex items-center space-x-3 transition-all duration-300 transform translate-x-full opacity-0`;
    toast.innerHTML = `<i class="fa-solid ${icons[type]}"></i> <span class="text-sm font-medium">${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
    }, 10);
    
    setTimeout(() => {
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function toggleLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.toggle('hidden', !show);
}

function openModal(id) { 
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('hidden'); 
}

function closeModal(id) { 
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('hidden'); 
}

// --- Navigation Logic ---
function showSection(sectionId) {
    console.log(`[Nav] Switching to section: ${sectionId}`);
    
    // 1. Hide all sections
    const sections = ['clients', 'payments', 'global_payments', 'subscriptions', 'master_control', 'logs'];
    sections.forEach(s => {
        const el = document.getElementById(`section-${s}`);
        if (el) el.classList.add('hidden');
    });

    // 2. Show target section
    const target = document.getElementById(`section-${sectionId}`);
    if (target) {
        target.classList.remove('hidden');
    } else {
        console.error(`Section ${sectionId} not found in DOM`);
        return;
    }

    // 3. Update Sidebar Links
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.classList.remove('active');
        if (link.id === `link-${sectionId}`) {
            link.classList.add('active');
        }
    });

    // 4. Update Header Title
    const titleMap = {
        'clients': 'Gestión de Clientes',
        'payments': 'Cobros y Enlaces de Pago',
        'global_payments': 'Monitoreo Global de Pagos',
        'subscriptions': 'Planes Recurrentes',
        'master_control': 'Master Control Plane',
        'logs': 'Logs Infra API'
    };
    document.getElementById('section-title').innerText = titleMap[sectionId] || 'Panel de Control';

    // 5. Show/Hide Client Selector
    const selector = document.getElementById('client-selector-container');
    if (selector) {
        // Show selector for payments and subscriptions
        const needsClient = ['payments', 'subscriptions'].includes(sectionId);
        selector.classList.toggle('hidden', !needsClient);
    }

    // 6. Special Loaders
    if (sectionId === 'master_control') {
        loadMasterTenants();
    } else if (sectionId === 'logs') {
        loadLogs();
    }
}

async function loadLogs() {
    const logsContent = document.getElementById('logs-content');
    if (!logsContent) return;
    logsContent.innerText = 'Cargando...';
    try {
        const data = await apiFetch('/api/admin/subscriptions');
        logsContent.innerText = JSON.stringify(data, null, 2);
    } catch (e) {
        logsContent.innerText = 'Error cargando logs: ' + e.message;
    }
}

// --- Master Control Plane ---
const MASTER_FEATURES = {
    'stock.pro_reports': { name: 'Reportes Avanzados', icon: 'fa-chart-line', group: 'Stock Pro' },
    'stock.extra_credits': { name: 'Créditos Extra', icon: 'fa-coins', group: 'Stock Pro' },
    'stock.bulk_import': { name: 'Importación Masiva', icon: 'fa-file-import', group: 'Stock Pro' },
    'whatsapp.bot_core': { name: 'Bot WhatsApp Core', icon: 'fa-robot', group: 'WhatsApp Hub' },
    'whatsapp.api_access': { name: 'Acceso API WhatsApp', icon: 'fa-plug', group: 'WhatsApp Hub' },
    'whatsapp.multi_agent': { name: 'Multi-Agente', icon: 'fa-users-gear', group: 'WhatsApp Hub' },
    'gateway.premium_support': { name: 'Soporte Premium', icon: 'fa-headset', group: 'General' },
};

async function loadMasterTenants() {
    try {
        toggleLoading(true);
        const data = await apiFetch('/clients');
        const tbody = document.getElementById('master-tenants-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        data.clients.forEach(c => {
            tbody.innerHTML += `
                <tr class="border-b hover:bg-slate-50 transition-colors">
                    <td class="p-4 text-sm font-mono text-slate-500">${c.global_tenant_id || c.id}</td>
                    <td class="p-4 text-sm font-bold">${c.name}</td>
                    <td class="p-4 text-sm">
                        <span class="${c.account_status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'} px-2 py-1 rounded-full text-xs font-semibold">
                            ${c.account_status}
                        </span>
                    </td>
                    <td class="p-4 text-right">
                        <button onclick="openEntitlementsModal('${c.global_tenant_id || c.id}')" class="bg-blue-600 text-white px-3 py-1 rounded-lg text-xs font-medium hover:bg-blue-700 transition-all">
                            <i class="fa-solid fa-key mr-1"></i> Gestionar Servicios
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (e) {
        notify('Error cargando tenants maestros: ' + e.message, 'error');
    } finally {
        toggleLoading(false);
    }
}

async function openEntitlementsModal(tenantId) {
    document.getElementById('entitlements-tenant-id').innerText = tenantId;
    const grid = document.getElementById('entitlements-grid');
    grid.innerHTML = '<div class="col-span-full text-center p-8 text-slate-400 italic">Cargando privilegios...</div>';
    openModal('modal-entitlements');
    
    try {
        const data = await apiFetch(`/api/master/license/audit/${tenantId}`, 'GET');
        const activeFeatures = data.data.map(f => f.feature_id);
        grid.innerHTML = '';
        
        const groups = {};
        Object.entries(MASTER_FEATURES).forEach(([id, info]) => {
            if (!groups[info.group]) groups[info.group] = [];
            groups[info.group].push({ id, ...info });
        });
        
        for (const [group, features] of Object.entries(groups)) {
            grid.innerHTML += `<div class="col-span-full"><h4 class="text-sm font-bold text-slate-400 uppercase mb-3">${group}</h4></div>`;
            features.forEach(f => {
                const isActive = activeFeatures.includes(f.id);
                grid.innerHTML += `
                    <div class="flex items-center justify-between p-4 bg-slate-50 rounded-xl border hover:border-blue-300 transition-all">
                        <div class="flex items-center space-x-3">
                            <div class="w-8 h-8 rounded-lg bg-white shadow-sm flex items-center justify-center text-blue-600">
                                <i class="fa-solid ${f.icon}"></i>
                            </div>
                            <span class="text-sm font-medium text-slate-700">${f.name}</span>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" class="sr-only peer" ${isActive ? 'checked' : ''} 
                                onchange="toggleEntitlement('${tenantId}', '${f.id}', this.checked)">
                            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>
                `;
            });
        }
    } catch (e) {
        notify('Error cargando licencias: ' + e.message, 'error');
    }
}

async function toggleEntitlement(tenantId, featureId, isActive) {
    const endpoint = isActive ? '/api/master/license/grant' : '/api/master/license/revoke';
    try {
        await apiFetch(endpoint, 'POST', { tenant_id: tenantId, feature_id: featureId });
        notify(`Servicio ${isActive ? 'activado' : 'desactivado'} correctamente`, 'success');
    } catch (e) {
        notify('Error al cambiar privilegio: ' + e.message, 'error');
        openEntitlementsModal(tenantId);
    }
}

// --- Client Management ---
async function loadClients() {
    try {
        const data = await apiFetch('/clients');
        const grid = document.getElementById('clients-grid');
        if (!grid) return;
        grid.innerHTML = '';
        
        data.clients.forEach(c => {
            const statusColor = c.account_status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700';
            grid.innerHTML += `
                <div class="bg-white p-6 rounded-xl shadow-sm border hover:shadow-md transition-all">
                    <div class="flex items-center space-x-4">
                        <div class="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-lg">
                            ${c.name.charAt(0)}
                        </div>
                        <div>
                            <h4 class="font-bold text-slate-800">${c.name}</h4>
                            <p class="text-sm text-slate-500">${c.email}</p>
                        </div>
                    </div>
                    <div class="mt-4 flex gap-2">
                        <span class="text-[10px] font-bold uppercase px-2 py-1 rounded ${c.has_whatsapp_hub ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-400'}">WA Hub</span>
                        <span class="text-[10px] font-bold uppercase px-2 py-1 rounded ${c.has_stock_pro ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-400'}">Stock Pro</span>
                        <span class="text-[10px] font-bold uppercase px-2 py-1 rounded ${statusColor}">${c.account_status}</span>
                    </div>
                    <div class="mt-6 flex justify-between items-center">
                        <span class="text-xs font-medium px-2 py-1 bg-slate-100 text-slate-600 rounded">ID: ${c.id}</span>
                        <div class="flex space-x-2">
                            <button onclick="updateStatus(${c.id}, '${c.account_status}')" class="text-xs bg-slate-200 text-slate-700 px-2 py-1 rounded hover:bg-slate-300 transition-all">
                                ${c.account_status === 'active' ? 'Suspender' : 'Activar'}
                            </button>
                            <button onclick="provisionClient(${c.id})" class="text-xs bg-slate-800 text-white px-2 py-1 rounded hover:bg-black transition-all">Activar</button>
                            <button onclick="editClient(${c.id})" class="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded hover:bg-blue-200 transition-all">Editar</button>
                            <button onclick="selectClient(${c.id}, '${c.name}')" class="text-blue-600 text-sm font-semibold hover:underline">Gestionar →</button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        const select = document.getElementById('active-client-select');
        if (select) {
            select.innerHTML = '<option value="">Seleccionar Cliente...</option>';
            data.clients.forEach(c => {
                select.innerHTML += `<option value="${c.id}">${c.name}</option>`;
            });
        }
    } catch (e) {
        notify('Error cargando clientes: ' + e.message, 'error');
    }
}

async function editClient(clientId) {
    try {
        const data = await apiFetch('/clients');
        const client = data.clients.find(c => c.id === clientId);
        if (!client) throw new Error('Cliente no encontrado');

        const form = document.getElementById('form-edit-client');
        form.elements['client_id'].value = client.id;
        form.elements['name'].value = client.name;
        form.elements['email'].value = client.email;
        form.elements['access_token'].value = client.access_token || '';
        form.elements['public_key'].value = client.public_key || '';
        form.elements['client_id_mp'].value = client.client_id || '';
        openModal('modal-edit-client');
    } catch (e) {
        notify('Error al cargar datos del cliente: ' + e.message, 'error');
    }
}

async function provisionClient(clientId) {
    if (!confirm('¿Deseas activar este cliente en todas las plataformas?')) return;
    try {
        await apiFetch('/provision', 'POST', { client_id: clientId, platforms: ['whatsapp', 'stock'] });
        loadClients();
        notify('Cliente provisionado exitosamente en WA Hub y Stock Pro', 'success');
    } catch (e) {
        notify('Error al provisionar: ' + e.message, 'error');
    }
}

async function updateStatus(clientId, currentStatus) {
    const newStatus = currentStatus === 'active' ? 'suspended' : 'active';
    if (!confirm(`¿Cambiar estado del cliente a ${newStatus}?`)) return;
    try {
        await apiFetch(`/clients/${clientId}/status`, 'PATCH', { status: newStatus });
        loadClients();
        notify(`Cliente ${newStatus === 'active' ? 'activado' : 'suspendido'} correctamente`, 'success');
    } catch (e) {
        notify('Error al actualizar estado: ' + e.message, 'error');
    }
}

function selectClient(id, name) {
    const select = document.getElementById('active-client-select');
    if (select) select.value = id;
    activeClientId = id;
    showSection('payments');
}

async function updateActiveClient() {
    activeClientId = document.getElementById('active-client-select').value;
    if (activeClientId) loadPayments();
}

// --- Payments & Subscriptions ---
async function loadPayments() {
    if (!activeClientId) {
        const tbody = document.getElementById('payments-table-body');
        if (tbody) tbody.innerHTML = '<tr><td colspan="5" class="p-8 text-center text-slate-400 italic">Por favor, selecciona un cliente primero.</td></tr>';
        return;
    }
    try {
        const data = await apiFetch(`/payments/${activeClientId}`);
        const tbody = document.getElementById('payments-table-body');
        if (!tbody) return;
        tbody.innerHTML = '';
        data.payments.forEach(p => {
            const statusColor = p.status === 'approved' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700';
            tbody.innerHTML += `
                <tr class="border-b hover:bg-slate-50 transition-colors">
                    <td class="p-4 text-sm font-medium">#${p.id}</td>
                    <td class="p-4 text-sm font-bold">$${p.amount}</td>
                    <td class="p-4 text-sm">
                        <span class="${statusColor} px-2 py-1 rounded-full text-xs font-semibold">${p.status}</span>
                    </td>
                    <td class="p-4 text-sm text-slate-500">${new Date(p.created_at).toLocaleDateString()}</td>
                    <td class="p-4 text-right space-x-2">
                        <a href="${p.init_point}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm font-medium">Link $ightarrow$</a>
                        <button onclick="showQR('${p.init_point}')" class="text-purple-600 hover:text-purple-800 text-sm font-medium">QR</button>
                    </td>
                </tr>
            `;
        });
    } catch (e) {
        console.error(e);
    }
}

function showQR(url) {
    const qrImg = document.getElementById('qr-image');
    if (qrImg) qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(url)}`;
    openModal('modal-qr');
}

async function loadSubscriptions() {
    const grid = document.getElementById('subscriptions-grid');
    if (!grid) return;
    
    grid.innerHTML = '<div class="col-span-full p-8 text-center text-slate-400 italic">Cargando suscripciones...</div>';
    
    try {
        const data = await apiFetch('/api/admin/subscriptions');
        grid.innerHTML = '';
        
        if (data.subscriptions.length === 0) {
            grid.innerHTML = '<div class="col-span-full p-8 text-center text-slate-400 italic">No hay dueños registrados.</div>';
            return;
        }
        
        data.subscriptions.forEach(s => {
            const statusColor = s.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700';
            grid.innerHTML += `
                <div class="bg-white p-6 rounded-xl shadow-sm border border-purple-100 hover:shadow-md transition-all">
                    <div class="flex justify-between items-start mb-4">
                        <div class="w-10 h-10 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center"><i class="fa-solid fa-user"></i></div>
                        <span class="text-[10px] font-bold uppercase px-2 py-1 rounded ${statusColor}">${s.status}</span>
                    </div>
                    <h4 class="font-bold text-slate-800">${s.cliente_nombre || s.username}</h4>
                    <p class="text-sm text-slate-500 mb-4">Plan: ${s.plan.toUpperCase()}</p>
                    <div class="text-xs text-slate-400 flex justify-between">
                        <span>Expira: ${s.expiry_date ? new Date(s.expiry_date).toLocaleDateString() : 'N/A'}</span>
                    </div>
                </div>
            `;
        });
    } catch (e) {
        grid.innerHTML = `<div class="col-span-full p-8 text-center text-red-500">Error cargando suscripciones: ${e.message}</div>`;
        console.error('Error cargando suscripciones:', e);
    }
}

async function loadGlobalPayments() {
    try {
        const data = await apiFetch('/payments/all');
        const tbody = document.getElementById('global-payments-table-body');
        if (!tbody) return;
        tbody.innerHTML = '';
        if (!data.payments || data.payments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="p-8 text-center text-slate-400 italic">No hay pagos registrados en el sistema.</td></tr>';
            return;
        }
        data.payments.forEach(p => {
            const statusColor = p.status === 'approved' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700';
            tbody.innerHTML += `
                <tr class="border-b hover:bg-slate-50 transition-colors">
                    <td class="p-4 text-sm font-medium">#${p.id}</td>
                    <td class="p-4 text-sm font-semibold">${p.client_name}</td>
                    <td class="p-4 text-sm font-bold">$${p.amount}</td>
                    <td class="p-4 text-sm"><span class="${statusColor} px-2 py-1 rounded-full text-xs font-semibold">${p.status}</span></td>
                    <td class="p-4 text-sm text-slate-500">${new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
            `;
        });
    } catch (e) {
        notify('Error cargando pagos globales: ' + e.message, 'error');
    }
}

// --- API Base ---
async function apiFetch(endpoint, method = 'GET', body = null) {
    console.log(`[API] ${method} ${endpoint}`, body);
    toggleLoading(true);
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (body) options.body = JSON.stringify(body);
        const res = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error en la solicitud');
        return data;
    } finally {
        toggleLoading(false);
    }
}

// --- Form Handlers ---
async function handleClientCreate(e) {
    e.preventDefault();
    console.log('[Form] Creating client...');
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    try {
        await apiFetch('/clients', 'POST', data);
        closeModal('modal-client');
        loadClients();
        notify('Cliente creado con éxito', 'success');
    } catch (e) {
        notify('Error: ' + e.message, 'error');
    }
}

async function handleClientEdit(e) {
    e.preventDefault();
    console.log('[Form] Editing client...');
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const clientId = data.client_id;
    delete data.client_id;
    if (data.client_id_mp) {
        data.client_id = data.client_id_mp;
        delete data.client_id_mp;
    }
    try {
        await apiFetch(`/clients/${clientId}`, 'PATCH', data);
        closeModal('modal-edit-client');
        loadClients();
        notify('Cliente actualizado con éxito', 'success');
    } catch (e) {
        notify('Error al actualizar cliente: ' + e.message, 'error');
    }
}

async function handlePaymentCreate(e) {
    e.preventDefault();
    console.log('[Form] Creating payment...');
    if (!activeClientId) return notify('Selecciona un cliente primero', 'warning');
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    data.client_id = parseInt(activeClientId);
    data.amount = parseFloat(data.amount);
    try {
        await apiFetch('/payments', 'POST', data);
        closeModal('modal-payment');
        loadPayments();
        notify(`¡Pago generado! Ya puedes abrir el Link o el QR desde la tabla.`, 'success');
    } catch (e) {
        notify('Error: ' + e.message, 'error');
    }
}

async function handleSubscriptionCreate(e) {
    e.preventDefault();
    console.log('[Form] Creating subscription...');
    if (!activeClientId) return notify('Selecciona un cliente primero', 'warning');
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    data.client_id = parseInt(activeClientId);
    data.amount = parseFloat(data.amount);
    try {
        await apiFetch('/subscriptions', 'POST', data);
        closeModal('modal-subscription');
        loadSubscriptions();
        notify('Suscripción activada con éxito', 'success');
    } catch (e) {
        notify('Error: ' + e.message, 'error');
    }
}

// --- Initialization ---
function init() {
    console.log('[System] Initializing Application...');
    
    const forms = [
        { id: 'form-client', handler: handleClientCreate },
        { id: 'form-edit-client', handler: handleClientEdit },
        { id: 'form-payment', handler: handlePaymentCreate },
        { id: 'form-subscription', handler: handleSubscriptionCreate }
    ];

    forms.forEach(formConfig => {
        const formEl = document.getElementById(formConfig.id);
        if (formEl) {
            console.log(`[System] Binding event to ${formConfig.id}`);
            formEl.addEventListener('submit', formConfig.handler);
        } else {
            console.warn(`[System] Form ${formConfig.id} not found in DOM`);
        }
    });

    // Default view
    showSection('clients');
    loadClients();
}

window.onload = init;
