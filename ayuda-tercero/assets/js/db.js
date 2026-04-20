// DB.js - Archivo de simulación de Base de Datos para el prototipo
// Esta base de datos sincroniza automáticamente la información entre diferentes páginas HTML usando LocalStorage.

const DB = {
    init: function () {
        if (!localStorage.getItem('db_prestamos')) {
            // Setup incial de prueba (Seed Data)
            localStorage.setItem('db_prestamos', JSON.stringify([
                { id: 'CR-1102', nombre: 'Juan Pérez', tipo: 'Personal', score: '95/100', monto: '$800 (6 meses)', status: 'Pendiente' }
            ]));
        }
        if (!localStorage.getItem('db_marketplace')) {
            localStorage.setItem('db_marketplace', JSON.stringify([
                { id: 'MK-3910', nombre: 'Pedro Santos', titulo: 'Silla de Ruedas Eléctrica', precio: '$450.00', status: 'En Revisión' },
                { id: 'MK-3911', nombre: 'Ana López', titulo: 'Medicamentos Controlados', precio: '$0.00', status: 'Reportado' }
            ]));
        }
        if (!localStorage.getItem('db_donaciones')) {
            localStorage.setItem('db_donaciones', JSON.stringify([
                { id: 'DN-2001', nombre: 'Carlos Valenzuela', titulo: 'Lote de Abrigos', categoria: 'ropa', status: 'Aprobado', celular: '8095550001' },
                { id: 'DN-2002', nombre: 'Marta R.', titulo: 'Libros Escolares', categoria: 'útil', status: 'En Revisión', celular: '8095550002' }
            ]));
        }
        if (!localStorage.getItem('db_stats')) {
            localStorage.setItem('db_stats', JSON.stringify({
                vidas_impactadas: 1245,
                donaciones_totales: 3892,
                co2_ahorrado: 450, // en kg
                casos_exitosos: 184
            }));
        }
        if (!localStorage.getItem('db_reputacion')) {
            localStorage.setItem('db_reputacion', JSON.stringify({
                puntos: 450,
                nivel: 'Gold',
                insignias: ['Donador Frecuente', 'Verificador IA', 'Líder Regional'],
                metas_proximas: [
                    { nombre: 'Héroe de la Red', progreso: 85 },
                    { nombre: 'Guardian Urbano', progreso: 30 }
                ]
            }));
        }
        if (!localStorage.getItem('db_casos')) {
            localStorage.setItem('db_casos', JSON.stringify([
                {
                    id: 'CS-SEED-1',
                    titulo: "Operación Pediátrica para Lucas",
                    categoria: "Emergencia Médica",
                    catKey: "medico",
                    story: "Lucas necesita una cirugía urgente de corazón. Cada grano de arena cuenta para recaudar los fondos médicos necesarios para su recuperación.",
                    raised: 7500,
                    meta: 10000,
                    img: "https://images.unsplash.com/photo-1584515933487-779824d29309?w=800",
                    status: 'Aprobado',
                    trustLevel: 'Gold',
                    dist: 1.2,
                    daysLeft: 2
                },
                {
                    id: 'CS-SEED-2',
                    titulo: "Reconstrucción Familia Díaz",
                    categoria: "Ayuda Familiar",
                    catKey: "familiar",
                    story: "La familia Díaz perdió su casa en un reciente incendio. Estamos solicitando apoyo económico y donaciones de muebles para recomenzar.",
                    raised: 1200,
                    meta: 8000,
                    img: "https://images.unsplash.com/photo-1532629345422-7515f3d16bb0?w=800",
                    status: 'Aprobado',
                    trustLevel: 'Silver',
                    dist: 4.5,
                    daysLeft: 12
                }
            ]));
        }
        if (!localStorage.getItem('db_impacto')) {
            localStorage.setItem('db_impacto', JSON.stringify([
                {
                    id: 'IMP-001',
                    nombre: "María Rodríguez",
                    ubicacion: "Santo Domingo Este",
                    historia: "Gracias a la silla de ruedas que recibí a través de la plataforma, ahora puedo salir al parque con mis nietos. La solidaridad me devolvió la libertad.",
                    videoUrl: "https://www.youtube.com/embed/dQw4w9WgXcQ", // Placeholder video
                    thumb: "https://images.unsplash.com/photo-1544027993-37dbfe43562a?w=800",
                    categoriaIcons: ["heart", "users"],
                    votos: 124,
                    fecha: "2024-03-15"
                },
                {
                    id: 'IMP-002',
                    nombre: "Juan Ramos",
                    ubicacion: "Santiago",
                    historia: "El préstamo Credifast me permitió comprar las herramientas para mi taller de carpintería. Hoy doy empleo a dos jóvenes de mi barrio.",
                    videoUrl: "", // No video, just story
                    thumb: "https://images.unsplash.com/photo-1581578731548-c64695ce6958?w=800",
                    categoriaIcons: ["tool", "briefcase"],
                    votos: 89,
                    fecha: "2024-03-20"
                }
            ]));
        }
    },

    // --- Módulo: Historias de Impacto (Testimonios) ---
    getImpacto: function () { return JSON.parse(localStorage.getItem('db_impacto')) || []; },
    saveImpacto: function (historia) {
        let list = this.getImpacto();
        historia.id = 'IMP-' + Math.floor(Math.random() * 9000 + 1000);
        historia.votos = 0;
        historia.fecha = new Date().toISOString().split('T')[0];
        list.push(historia);
        localStorage.setItem('db_impacto', JSON.stringify(list));
        return historia;
    },
    voteImpacto: function (id) {
        let list = this.getImpacto();
        let idx = list.findIndex(i => i.id === id);
        if (idx !== -1) {
            list[idx].votos++;
            localStorage.setItem('db_impacto', JSON.stringify(list));
        }
    },
    deleteImpacto: function (id) {
        let list = this.getImpacto();
        list = list.filter(i => i.id !== id);
        localStorage.setItem('db_impacto', JSON.stringify(list));
    },

    // --- Módulo: Estadísticas Globales ---
    getStats: function () { 
        return JSON.parse(localStorage.getItem('db_stats')) || { vidas_impactadas: 0, donaciones_totales: 0, co2_ahorrado: 0, casos_exitosos: 0 }; 
    },
    updateStats: function (key, increment = 1) {
        let stats = this.getStats();
        if (stats[key] !== undefined) {
            stats[key] += increment;
            localStorage.setItem('db_stats', JSON.stringify(stats));
        }
    },

    // --- Módulo: Reputación ---
    getReputation: function () {
        return JSON.parse(localStorage.getItem('db_reputacion')) || { puntos: 0, nivel: 'Silver', insignias: [], metas_proximas: [] };
    },
    addPoints: function (amount) {
        let rep = this.getReputation();
        rep.puntos += amount;
        if (rep.puntos > 500) rep.nivel = 'Gold';
        localStorage.setItem('db_reputacion', JSON.stringify(rep));
    },

    // --- Módulo: Préstamos (Credifast) ---
    getPrestamos: function () { return JSON.parse(localStorage.getItem('db_prestamos')) || []; },
    savePrestamo: function (prestamo) {
        let list = this.getPrestamos();
        prestamo.id = 'CR-' + Math.floor(Math.random() * 9000 + 1000);
        prestamo.status = 'Pendiente';
        list.push(prestamo);
        localStorage.setItem('db_prestamos', JSON.stringify(list));
        return prestamo;
    },
    updatePrestamoStatus: function (id, newStatus) {
        let list = this.getPrestamos();
        let idx = list.findIndex(i => i.id === id);
        if (idx !== -1) {
            list[idx].status = newStatus;
            localStorage.setItem('db_prestamos', JSON.stringify(list));
        }
    },

    // --- Módulo: Marketplace & Donaciones ---
    getMarketplace: function () { return JSON.parse(localStorage.getItem('db_marketplace')) || []; },
    saveMarketplace: function (item) {
        let list = this.getMarketplace();
        item.id = 'MK-' + Math.floor(Math.random() * 9000 + 1000);
        item.status = 'En Revisión';
        list.push(item);
        localStorage.setItem('db_marketplace', JSON.stringify(list));
        return item;
    },
    updateMarketplaceStatus: function (id, newStatus) {
        let list = this.getMarketplace();
        let idx = list.findIndex(i => i.id === id);
        if (idx !== -1) {
            list[idx].status = newStatus;
            localStorage.setItem('db_marketplace', JSON.stringify(list));
        }
    },

    // --- Módulo: Donaciones ---
    getDonaciones: function () { return JSON.parse(localStorage.getItem('db_donaciones')) || []; },
    saveDonacion: function (item) {
        let list = this.getDonaciones();
        item.id = 'DN-' + Math.floor(Math.random() * 9000 + 1000);
        item.status = 'En Revisión';
        list.push(item);
        localStorage.setItem('db_donaciones', JSON.stringify(list));
        return item;
    },
    updateDonacionStatus: function (id, newStatus) {
        let list = this.getDonaciones();
        let idx = list.findIndex(i => i.id === id);
        if (idx !== -1) {
            list[idx].status = newStatus;
            localStorage.setItem('db_donaciones', JSON.stringify(list));
        }
    },

    // --- Módulo: Casos Solidarios ---
    getCasos: function () { return JSON.parse(localStorage.getItem('db_casos')) || []; },
    saveCaso: function (caso) {
        let list = this.getCasos();
        caso.id = 'CS-' + Math.floor(Math.random() * 9000 + 1000);
        caso.status = 'En Revisión';
        
        // Simulación de Priorización IA
        const text = (caso.title + " " + caso.desc).toLowerCase();
        if (text.includes('urgente') || text.includes('cirugía') || text.includes('emergencia') || text.includes('crítico')) {
            caso.aiUrgency = 'High';
            caso.daysLeft = 3;
        } else {
            caso.aiUrgency = 'Normal';
            caso.daysLeft = 15;
        }

        list.push(caso);
        localStorage.setItem('db_casos', JSON.stringify(list));
        return caso;
    },
    updateCasoStatus: function (id, newStatus) {
        let list = this.getCasos();
        let idx = list.findIndex(i => i.id === id);
        if (idx !== -1) {
            list[idx].status = newStatus;
            localStorage.setItem('db_casos', JSON.stringify(list));
        }
    },
    updateCasoAmount: function (idOrTitle, amount) {
        let list = this.getCasos();
        let idx = list.findIndex(i => i.id === idOrTitle || i.titulo === idOrTitle);
        if (idx !== -1) {
            list[idx].raised = (parseFloat(list[idx].raised) || 0) + parseFloat(amount);
            localStorage.setItem('db_casos', JSON.stringify(list));
            return list[idx];
        }
        return null;
    }
};

DB.init();
