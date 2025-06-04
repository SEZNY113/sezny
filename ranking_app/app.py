from dataclasses import dataclass, field
from typing import List
import io
import csv
from flask import Flask, render_template, request, redirect, url_for

@dataclass(order=True)
class RiderResult:
    sort_index: int = field(init=False, repr=False)
    name: str
    time_seconds: int

    def __post_init__(self):
        self.sort_index = self.time_seconds

    def formatted_time(self) -> str:
        hrs, rem = divmod(self.time_seconds, 3600)
        mins, secs = divmod(rem, 60)
        return f"{int(hrs):02}:{int(mins):02}:{int(secs):02}"

class RaceRanking:
    def __init__(self):
        self.results: List[RiderResult] = []

    def add_result(self, name: str, hours: int, minutes: int, seconds: int) -> None:
        total_seconds = hours * 3600 + minutes * 60 + seconds
        self.results.append(RiderResult(name=name, time_seconds=total_seconds))

    def load_from_csv(self, file_like) -> None:
        file_like.seek(0)
        data = file_like.read()
        if isinstance(data, bytes):
            data = data.decode()
        reader = csv.reader(io.StringIO(data))
        for row in reader:
            if len(row) < 2:
                continue
            name = row[0].strip()
            parts = [int(p) for p in row[1].split(":")]
            if len(parts) == 3:
                h, m, s = parts
            elif len(parts) == 2:
                h, m = parts
                s = 0
            else:
                continue
            self.add_result(name, h, m, s)

    def get_rankings(self) -> List[RiderResult]:
        return sorted(self.results)

app = Flask(__name__)
ranking = RaceRanking()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            ranking.load_from_csv(file)
        return redirect(url_for('index'))
    return render_template('index.html', rankings=ranking.get_rankings())

if __name__ == '__main__':
    app.run(debug=True)
