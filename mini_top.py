import asyncio

import psutil
from austin_tui.view import View, ViewBuilder


def format_cmdline(cmdline):
    if not cmdline:
        return ""
    cmd, *args = cmdline
    args = " ".join(
        [arg if arg.startswith("-") else f"<b><opt>{arg}</opt></b>" for arg in args]
    )
    return f"<cmd>{cmd}</cmd> <args>{args}</args>"


class MiniTop(View):
    def on_quit(self, data=None):
        raise KeyboardInterrupt("quit signal")

    def on_pgdown(self, data=None):
        self.proc_view.scroll_down(self.table.height - 1)
        self.proc_view.refresh()
        return False

    def on_pgup(self, data=None):
        self.proc_view.scroll_up(self.table.height - 1)
        self.proc_view.refresh()
        return False

    def on_up(self, data=None):
        self.proc_view.scroll_up()
        self.proc_view.refresh()
        return False

    def on_down(self, data=None):
        self.proc_view.scroll_down()
        self.proc_view.refresh()
        return False

    async def update(self):
        while True:
            data = sorted(
                [
                    (
                        p.info["pid"],
                        p.info["cpu_percent"],
                        format_cmdline(p.info["cmdline"]),
                    )
                    for p in psutil.process_iter(["pid", "cpu_percent", "cmdline"])
                ],
                key=lambda x: x[1],
                reverse=True,
            )
            self.table.set_data(
                [
                    (
                        self.markup(f"<pid>{pid:8d}</pid>"),
                        self.markup(f"<b>{cpu:^10.2f}</b>"),
                        self.markup(cmdline),
                    )
                    for pid, cpu, cmdline in data
                ]
            )

            self.nprocs.set_text(str(len(data)))
            self.cpu.set_text(f"{psutil.cpu_percent():3.2f}")

            self.table.draw()
            self.root_widget.refresh()

            await asyncio.sleep(2)


def main():
    with open("mini-top.austinui") as austinui:
        view = ViewBuilder.from_stream(austinui)
        view.open()

    loop = asyncio.get_event_loop()

    try:
        loop.create_task(view.update())
        loop.run_forever()
    except KeyboardInterrupt:
        view.close()
        print("Bye!")


if __name__ == "__main__":
    main()
