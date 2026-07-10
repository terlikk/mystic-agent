import { type ComponentPropsWithoutRef, type ReactNode } from "react"
import { ArrowRightIcon } from "@radix-ui/react-icons"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface BentoGridProps extends ComponentPropsWithoutRef<"div"> {
  children: ReactNode
  className?: string
}

interface BentoCardProps extends ComponentPropsWithoutRef<"div"> {
  name: string
  className: string
  background: ReactNode
  Icon?: React.ElementType
  description: string
  eyebrow?: string
  href?: string
  cta?: string
}

const BentoGrid = ({ children, className, ...props }: BentoGridProps) => {
  return (
    <div
      className={cn(
        "grid w-full auto-rows-[24rem] grid-cols-3 gap-4",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

const BentoCard = ({
  name,
  className,
  background,
  Icon,
  description,
  eyebrow,
  href,
  cta,
  ...props
}: BentoCardProps) => (
  <div
    key={name}
    className={cn(
      "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-lg",
      "border border-line bg-panel transition-colors duration-300 hover:border-cyan/30",
      className
    )}
    {...props}
  >
    <div className="min-h-0 flex-1">{background}</div>
    <div className="p-5">
      <div className="flex transform-gpu flex-col gap-1.5">
        {eyebrow && (
          <span className="font-mono text-[10px] tracking-[0.2em] text-cyan uppercase">
            {eyebrow}
          </span>
        )}
        {Icon && (
          <Icon className="h-10 w-10 origin-left transform-gpu text-cyan transition-all duration-300 ease-in-out group-hover:scale-90" />
        )}
        <h3 className="font-heading text-xl font-bold text-foreground">
          {name}
        </h3>
        <p className="max-w-lg text-sm leading-relaxed text-dim">
          {description}
        </p>
      </div>

      {href && cta && (
        <div className="mt-3 flex w-full flex-row items-center">
          <Button
            variant="link"
            asChild
            size="sm"
            className="pointer-events-auto p-0 text-cyan"
          >
            <a href={href}>
              {cta}
              <ArrowRightIcon className="ms-2 h-4 w-4 rtl:rotate-180" />
            </a>
          </Button>
        </div>
      )}
    </div>

    <div className="pointer-events-none absolute inset-0 transform-gpu transition-all duration-300 group-hover:bg-cyan/[0.02]" />
  </div>
)

export { BentoCard, BentoGrid }
