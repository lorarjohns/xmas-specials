from halo import Halo
'''
a really dumb script
that wastes some time
to show how the cool spinner works
'''
spinner = Halo(text='ooo shiny')
spinner.start()
nums = [i**j for i in range(1000) for j in range(1000)]

spinner.succeed(text=f'All done! Calculated {len(nums)} numbers.')

__name__ == "__main__"
