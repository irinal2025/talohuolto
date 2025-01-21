function fetchTasks() {
    const sortBy = document.getElementById('sort_by').value;
    const order = document.getElementById('order').value;

    fetch(`/api/tasks?sort_by=${sortBy}&order=${order}`)
        .then(response => response.json())
        .then(data => {
            const tasksList = document.getElementById('tasksList');
            tasksList.innerHTML = '';

            if (data.tasks.length > 0) {
                data.tasks.forEach(task => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <strong>${task.task_name}</strong> | 
                        Kategoria: ${task.category} | 
                        Aloitus: ${task.start_date} | 
                        Päättyy: ${task.end_date} | 
                        Prioriteetti: <span class="priority-${task.priority.toLowerCase()}">${task.priority}</span>
                    `;

                    // Lisää "Muokkaa"-linkki, jos käyttäjä on ylläpitäjä
                    if (data.is_administrator) {
                        li.innerHTML += `
                            <span> | </span>
                            <a href="/dashboard/tasks/${task.id}/edit">Muokkaa <i class="fa-solid fa-angles-right"></i></a>
                        `;
                    }

                    tasksList.appendChild(li);
                });
            } else {
                tasksList.innerHTML = '<p>Ei tehtäviä listattavana.</p>';
            }
        });
}

// Kuuntele valikon muutoksia
document.getElementById('sort_by').addEventListener('change', fetchTasks);
document.getElementById('order').addEventListener('change', fetchTasks);

// Lataa tehtävät aluksi
fetchTasks();
