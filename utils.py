from datetime import datetime, timedelta, time


def delta_times(start_time, end_time):
    today = datetime.today().date()
    start = datetime.combine(today, start_time)
    end = datetime.combine(today, end_time)

    if end < start:
        end += timedelta(days=1)

    diff = end - start
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return time(hours, minutes, seconds)



def group_time_tasks(tasks):
    tasks = tasks.copy()
    res = []

    while tasks:
        # Берем первую задачу из оставшихся
        current_task = tasks.pop(0)
        current_group = [current_task]

        # Проверяем остальные задачи на возможность добавления в группу
        i = 0
        while i < len(tasks):
            task = tasks[i]
            can_add = True

            # Проверяем, что задача не пересекается ни с одной из задач в группе
            for grouped_task in current_group:
                if are_tasks_overlapping(task, grouped_task):
                    can_add = False
                    break

            if can_add:
                current_group.append(task)
                tasks.pop(i)  # Удаляем задачу из списка, так как она добавлена в группу
            else:
                i += 1  # Переходим к следующей задаче, если текущую нельзя добавить

        res.append(current_group)

    # Сортируем группы по убыванию количества задач
    return sorted(res, key=lambda x: len(x), reverse=True)


from datetime import datetime


def are_tasks_overlapping(task1, task2):
    """Проверяет, пересекаются ли две задачи по времени.
    Учитывает, что задачи без end_time длятся 0 секунд (мгновенные)."""
    start1 = datetime.strptime(task1['start_time'], "%H:%M:%S").time()
    end1 = datetime.strptime(task1['end_time'], "%H:%M:%S").time() if task1.get('end_time') else start1
    start2 = datetime.strptime(task2['start_time'], "%H:%M:%S").time()
    end2 = datetime.strptime(task2['end_time'], "%H:%M:%S").time() if task2.get('end_time') else start2

    # Если обе задачи мгновенные (end_time = start_time)
    if end1 == start1 and end2 == start2:
        return start1 == start2  # пересекаются только если start_time совпадает

    # Если первая задача мгновенная, проверяем, попадает ли её start_time в интервал второй
    if end1 == start1:
        return start2 <= start1 <= end2

    # Если вторая задача мгновенная, проверяем, попадает ли её start_time в интервал первой
    if end2 == start2:
        return start1 <= start2 <= end1

    # Обычная проверка пересечения интервалов
    return max(start1, start2) < min(end1, end2)
