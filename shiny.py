from halo import Halo

spinner = Halo(text='ooo shiny')
spinner.start()
nums = [i**j for i in range(1000) for j in range(1000)]

spinner.succeed(text=f'Printing {len(nums)} articles. ===> Done')

__name__ == "__main__"